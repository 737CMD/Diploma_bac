import sys
import os
import json
import numpy as np
import ansys.fluent.core as pyfluent

import airfoil_generator
import icem_runner as ir
import fluent_runner 

script_dir = os.path.dirname(os.path.abspath(__file__))
icem_exe = r"E:\Program files\ANSYS Inc\v242\icemcfd\win64_amd\bin\icemcfd.bat"
fluent_case_path = os.path.join(script_dir, "optimization_setup.cas.h5")
rpl_script_path = os.path.join(script_dir, "airfoil_mesh_script.rpl")
mesh_file = os.path.join(script_dir, "geom.msh")
report_file_name = os.path.join(script_dir, "curropt-report.out")

def parse_dakota_params(params_file):
    with open(params_file, 'r') as f:
        lines = f.readlines()
    params = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2 and parts[1].startswith('x'):
            params.append(float(parts[0]))
    return np.array(params)

def write_results(results_file, objective=None, failed=False):
    with open(results_file, 'w') as f:
        if failed:
            f.write("FAIL objective_fn\n")
        else:
            f.write(f"{objective} objective_fn\n")

def main(params_file, results_file):
    params = parse_dakota_params(params_file)
    
    json_file = os.path.join(script_dir, 'shared_data.json')
    if not os.path.exists(json_file):
        print("[Worker] ОШИБКА: Файл shared_data.json не найден. FAIL.")
        write_results(results_file, failed=True)
        return
        
    with open(json_file, 'r') as f:
        shared_data = json.load(f)
        
    cfg = shared_data['config']

    print(f"\n[Worker] Входные параметры: {np.round(params, 4)}")

    # 1. Генерация профиля
    r_forw = params[0] * cfg['r_bound']
    fine_function = 0
    if r_forw < cfg['min_r_forw']: 
        fine_function += (cfg['min_r_forw'] - r_forw) * 1000
        
    pts = cfg['points']
    up_coords = params[1:pts+1] * cfg['point_bound']
    down_coords = params[pts+1:-1] * cfg['point_bound']
    teta = params[-1] * cfg['teta_bound']
    
    airfoil = airfoil_generator.airfoil_structured(
        r_forw, up_coords, down_coords, teta, cfg['dy_te']
    )
    
    smooth_penalty = 2000.0 + 100.0 * np.sum(params**2)

    if airfoil.self_intersect():
        print(f"[Worker] Самопересечение. Штраф: {smooth_penalty:.1f}")
        write_results(results_file, objective=smooth_penalty)
        return
    airfoil.correct_thick(cfg['min_thick'])
    airfoil.create_icem_file(500)
    if not ir.run_icem(icem_exe, rpl_script_path):
        print(f"[Worker] Ошибка сетки ICEM. Штраф: {smooth_penalty:.1f}")
        write_results(results_file, objective=smooth_penalty)
        return

    try:   
        session = pyfluent.launch_fluent(
        processor_count=10, 
        dimension=2, 
        cwd=script_dir, 
        precision="double", 
        case_file_name=fluent_case_path,
        show_gui=False, 
        start_transcript=False
    )
        
        cl, cd = fluent_runner.run_fluent_simulation(
            session, cfg['target_cl'], cfg['cl_tol'], cfg['cd_tol'], 
            cfg['Mach'], cfg['Re'], cfg['T'], cfg['conv_iter'], 
            mesh_file, report_file_name
        )
        
        # Если Fluent развалился или сработал быстрый отсев (None, None)
        if cl is None or cd is None or cd >= 1:
            print(f"[Worker] Отсев Fluent. Штраф: {smooth_penalty:.1f}")
            write_results(results_file, objective=smooth_penalty)
            return
            
    except Exception as e:
        print(f"[Worker] Сбой связи: {e}. Штраф: {smooth_penalty:.1f}")
        write_results(results_file, objective=smooth_penalty)
        return
    finally:
    # 3. ГАРАНТИРОВАННОЕ УБИЙСТВО ПРОЦЕССА
        if session is not None:
            try:
                session.exit()
            except:
                pass
    # Если всё прошло идеально:
    objective_value = (cd * 10000 + 10 * fine_function**2)
    print(f"[Worker] Успех! Cd*10k = {cd*10000:.2f}. Целевая: {objective_value:.2f}")
    write_results(results_file, objective=objective_value)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])