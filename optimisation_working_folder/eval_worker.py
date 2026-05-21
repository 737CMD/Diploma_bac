import sys
import os
import json
import numpy as np
import ansys.fluent.core as pyfluent
from scipy.optimize import fsolve
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

def airfoil_distance(airfoil, zero_airfoil):
    u1, d1 = airfoil.coords(100)
    u0, d0 = zero_airfoil.coords(100)
    dist = np.sum((np.array(u1) - np.array(u0))**2) + np.sum((np.array(d1) - np.array(d0))**2)
    return dist

def create_airfoil_from_norm_params(params, r_bound, point_bound, teta_bound, points, dy_te, min_thick):
    r_forw = params[0]*r_bound
    up_coords = params[1:points+1]*point_bound
    down_coords = params[points+1:-1]*point_bound
    teta = params[-1]*teta_bound
    airfoil = airfoil_generator.airfoil_structured(r_forw, up_coords, down_coords, teta, dy_te, min_thick)
    return airfoil

def create_airfoil_from_norm_params_thick(params, r_bound, point_bound, teta_bound, points, dy_te, thick, var_point):
    succ = True
    def func(x):
        current_params = np.insert(params, var_point, x)
        airfoil = create_airfoil_from_norm_params(current_params, r_bound, point_bound, teta_bound, points, dy_te, min_thick=-1)
        return airfoil.thick()[0] - thick
    x0 = 1
    x = fsolve(func, x0)
    if x < -1 or x > 1:
        print(f"Невозможно достичь заданной толщины {thick}%. Решение вышло за пределы допустимых значений")
        succ = False
    current_params = np.insert(params, var_point, x)
    airfoil = create_airfoil_from_norm_params(current_params, r_bound, point_bound, teta_bound, points, dy_te, min_thick=-1)
    return succ, airfoil

def main(params_file, results_file):
    params = parse_dakota_params(params_file)
    fine_function = 0.0
    json_file = os.path.join(script_dir, 'shared_data.json')
    if not os.path.exists(json_file):
        print("[Worker] ОШИБКА: Файл shared_data.json не найден. FAIL.")
        write_results(results_file, failed=True)
        return
        
    with open(json_file, 'r') as f:
        shared_data = json.load(f)
        
    cfg = shared_data['config']

    print(f"\n[Worker] Входные параметры: {np.round(params, 4)}")
    r_bound = cfg['min_r_forw']*10
    # 1. Генерация профиля
    succ, airfoil = create_airfoil_from_norm_params_thick(params, r_bound, cfg['point_bound'], cfg['teta_bound'], cfg['points'], cfg['dy_te'], cfg['min_thick'], var_point=2)
    sym_params = np.array([0.375, 0.17, -0.4, 0.5])
    _, sym_airfoil = create_airfoil_from_norm_params_thick(sym_params, r_bound, cfg['point_bound'], cfg['teta_bound'], 2, cfg['dy_te'], thick = 12, var_point = 1)
    delta_params = airfoil_distance(airfoil, sym_airfoil)
    smooth_penalty = 1500 + 3000 * delta_params
    if not succ: 
        print(f"[Worker] Невозможно достичь заданной толщины в заданных границах. Штраф: {smooth_penalty:.1f}")
        write_results(results_file, objective=smooth_penalty)
        return
    if airfoil.self_intersect():
        print(f"[Worker] Самопересечение. Штраф: {smooth_penalty:.1f}")
        write_results(results_file, objective=smooth_penalty)
        return
    #airfoil.correct_thick(cfg['min_thick']) #не трогаем для EGO профиля, чтобы не ломать модель
    #if airfoil.thick()[0] < cfg['min_thick']:
    #    fine_function += (cfg['min_thick'] - airfoil.thick()[0])**2 * 1000
    #    if fine_function > smooth_penalty:
    #        print(f"[Worker] Сильно недостаточная толщина: {airfoil.thick()[0]} Штраф: {smooth_penalty:.1f}")
    #        write_results(results_file, objective=smooth_penalty)
    #        return
    #if airfoil.thick()[0] > 19:
    #    print(f"[Worker] Сильно избыточная толщина: {airfoil.thick()[0]} Штраф: {smooth_penalty:.1f}")
    #    write_results(results_file, objective=smooth_penalty)
    #    return
    airfoil.create_icem_file(500)
    if not ir.run_icem(icem_exe, rpl_script_path):
        print(f"[Worker] Ошибка сетки ICEM. Штраф: {smooth_penalty:.1f}")
        write_results(results_file, objective=smooth_penalty)
        return
    session = None
    try:   
        session = pyfluent.launch_fluent(
        processor_count=10, 
        dimension=2, 
        cwd=script_dir, 
        precision="double", 
        case_file_name=fluent_case_path,
        ui_mode="no_gui_or_graphics", 
        start_transcript=False
    )
        
        cl, cd = fluent_runner.run_fluent_simulation(
            session, cfg['target_cl'], cfg['cl_tol'], cfg['cd_tol'], 
            cfg['Mach'], cfg['Re'], cfg['T'], cfg['conv_iter'], 
            mesh_file, report_file_name
        )
        
        # Если Fluent развалился или сработал быстрый отсев (None, None)
        if cl is None or cd is None:
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
    objective_value = (cd * 10000 + fine_function)
    if objective_value > smooth_penalty:
        print(f"[Worker] Посчитан плохой профиль. Cd*10k = {cd*10000:.2f}. Целевая: {objective_value:.2f}. Штраф для гладкости: {smooth_penalty:.1f}")
        write_results(results_file, objective=smooth_penalty)
    else:
        print(f"[Worker] Успех! Cd*10k = {cd*10000:.2f}. Целевая: {objective_value:.2f}")
        write_results(results_file, objective=objective_value)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])