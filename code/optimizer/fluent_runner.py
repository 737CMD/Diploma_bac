import ansys.fluent.core as pyfluent
import numpy as np

def check_convergence(file_name, tol_cya, tol_cxa, conv_iter):
    """
    Проверяет сходимость Cya и Cxa по последним conv_iter итерациям.
    Возвращает: (bool, float, float) -> (статус сходимости, среднее Cya, среднее Cxa)
    """
    try:
        # 1. Чтение и парсинг файла в numpy array
        with open(file_name, 'r') as f:
            raw = (line.replace('"', '').replace('(', '').replace(')', '').split() for line in f)
            # Фильтруем только строки с данными (где первый элемент - число)
            data = np.array([row for row in raw if row and row[0].isdigit()], dtype=float)
        # Проверка на достаточность данных
        if data.shape[0] < conv_iter:
            print("Недостаточно данных для расчета среднего.")
            return False, 0.0, 0.0
        # Столбцы: 1 -> Cya, 2 -> Cxa
        cya, cxa = data[:, 1], data[:, 2]
        last_cya, last_cxa = cya[-conv_iter*2+1:], cxa[-conv_iter*2+1:],
        # 2. Вычисление скользящего среднего через свертку
        kernel = np.ones(conv_iter) / conv_iter
        # mode='valid' означает, что среднее считается только там, где окно полностью перекрывает данные
        last_ma_cya = np.convolve(last_cya, kernel, mode='valid')
        last_ma_cxa = np.convolve(last_cxa, kernel, mode='valid')      
        # Результирующие средние (последняя точка скользящего среднего)
        final_cya = last_ma_cya[-1]
        final_cxa = last_ma_cxa[-1]
        # 4. Проверка: все средние в окне должны быть в пределах tol от финального среднего
        cya_ok = np.all(np.abs(last_ma_cya - final_cya) <= tol_cya)
        cxa_ok = np.all(np.abs(last_ma_cxa - final_cxa) <= tol_cxa)
        return (cya_ok and cxa_ok), final_cya, final_cxa
    except Exception as e:    
        return False, 0.0, 0.0

def run_fluent_simulation(solver_session, target_cya, cya_tol, cxa_tol, Mach, Re, T, conv_iter, mesh_file, file_name):
    solver_session.settings.file.replace_mesh(file_name = mesh_file)
    solver_session.settings.parameters.input_parameters.expression["alpha"].value = 0
    solver_session.settings.parameters.input_parameters.expression["Re"].value = Re
    solver_session.settings.parameters.input_parameters.expression["Mach"].value = Mach
    solver_session.settings.parameters.input_parameters.expression["Temperature"].value = T
    solver_session.settings.solution.initialization.initialize()
    solver_session.settings.solution.initialization.hybrid_initialize()
    solver_session.settings.setup.reference_values.compute(from_zone_type = 'pressure-far-field', from_zone_name = 'inlet')
    solver_session.tui.solve.report_files.clear_data('integral_char')
    total_iterations = 0
    def run_calc(step_iter, cya_tol, cxa_tol):
        nonlocal total_iterations
        solver_session.settings.solution.run_calculation.iterate(iter_count=step_iter)
        total_iterations += step_iter
        converged, cya, cxa = check_convergence(file_name, cya_tol, cxa_tol, conv_iter)  
        while not converged: 
            solver_session.settings.solution.run_calculation.iterate(iter_count=step_iter)
            total_iterations += step_iter
            converged, cya, cxa = check_convergence(file_name, cya_tol, cxa_tol, conv_iter)
            if total_iterations >= 2500: return target_cya, 1
        return cya, cxa
    cya, cxa = run_calc(100, cya_tol, cxa_tol)
    if cya < 0: return cya, 0.5
    alpha_step = 0.5
    #метод Ньютона для решения 
    while(abs(cya-target_cya) > cya_tol):
        if total_iterations >= 2500: return cya, 0.5
        alpha_step *= -1
        curralpha = solver_session.settings.parameters.input_parameters.expression["alpha"].value()
        newalpha = curralpha + alpha_step
        solver_session.settings.parameters.input_parameters.expression["alpha"].value = newalpha
        newcya, newcxa = run_calc(50, cya_tol, cxa_tol)
        cya_a = (newcya - cya)/alpha_step
        newalpha = curralpha + (target_cya-cya)/cya_a
        solver_session.settings.parameters.input_parameters.expression["alpha"].value = newalpha
        cya, cxa = run_calc(50, cya_tol, cxa_tol)
    return cya, cxa