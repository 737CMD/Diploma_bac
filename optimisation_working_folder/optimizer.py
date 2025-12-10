import numpy as np
import matplotlib.pyplot as plt
import icem_runner as ir
import airfoil_generator 
import fluent_runner
from scipy.optimize import minimize


#Условия оптимизации 
Mach = 0.5
Re = 6e6
T = 300 #температура воздуха в Кельвинах

#Требования на профиль
min_thick = 8.0  #минимальная толщина профиля в процентах от хорды
target_cl = 0.5 #целевое значение Cl
min_r_forw = 0.01 #минимальный радиус кривизны передней кромки
points = 3 #количество точек на верхней и нижней поверхностях профиля (без учета точек передней и задней кромок)
dy_te = 0.0 #зазор в задней кромке

#Настройки расчета
solver = 'density' #выбор солвера: 'pressure' или 'density'
cl_tol = 0.005 #допустимое отклонение Cl от целевого значения при расчете Cd и требование по сходимости
сd_tol = 0.0001 #Ширина полосы допустимых для сходимости cx (рекомендуется оставить 1 count
conv_iter = 30 #Длина полосы, в которой проводится проверка сходимости
start_iter = 200 #Стартовое число итераций, после которых начинается перестановка alpha 


#Пути к файлам рабочим 
icem_exe = r"E:\Program files\ANSYS Inc\v242\icemcfd\win64_amd\bin\icemcfd.bat"
rpl_script_path = r"E:\tsagi_dipl\Diploma_bac\optimisation_working_folder\airfoil_mesh_script.rpl"
fluent_case_path = r"E:\tsagi_dipl\Diploma_bac\optimisation_working_folder\optimisation_preset.cas"

class optimizer: 
    #Класс-оптимизатор. В нем удобно хранить всякое барахло
    def __init__(self, show_im_afs = False):
        self.show_im_afs = show_im_afs
        self.params_history = np.array([])
        self.objective_history = np.array([])
        
    def create_airfoil_from_params(self, params):
        params = np.array(params)
        r_forw = params[0]
        if  r_forw < min_r_forw: r_forw = min_r_forw
        up_coords = params[1:points+1]
        down_coords = params[points+1:-1]
        airfoil = airfoil_generator.airfoil_structered(r_forw, up_coords, down_coords, dy_te, min_thick)
        return airfoil
    
    def logger(self, *, intermediate_result):
        current_params = intermediate_result.x
        current_objective = intermediate_result.fun
        self.params_history = np.append(self.params_history, [current_params], axis=0)
        self.objective_history = np.append(self.objective_history, current_objective)
        if self.show_im_afs:
            airfoil = self.create_airfoil_from_params(current_params)
            airfoil.plot_airfoil()
            plt.title(f"Current Objective: {current_objective:.6f}")
            plt.show()                

    def objective_function(self, params):
    
        airfoil = self.create_airfoil_from_params(params)

        if airfoil.self_intersect():
            print("Профиль самопересекается. Пропуск итерации.")
            return 1e6  # штраф за самопересечение
        # Сохранение координат профиля в файл для ICEM
        airfoil.create_icem_file(500)
        # Запуск ICEM для генерации сетки
        mesh_success = ir.run_icem(icem_exe, rpl_script_path)
        if not mesh_success:
            print("Ошибка при генерации сетки в ICEM. Пропуск итерации.")
            return 1e6  # штраф за ошибку сетки

        # Запуск Fluent для расчета аэродинамики
        cl, cd = fluent_runner.run_fluent_simulation(fluent_case_path, target_cl, cl_tol, Mach, Re, T, solver)
        if cl is None or cd is None:
            print("Ошибка при расчете в Fluent. Пропуск итерации.")
            return 1e6  # штраф за ошибку расчета    
        # Целевая функция: минимизация Cd при достижении целевого Cl
        objective_value = cd
        return objective_value
    
    def optimize(self, initial_params, method = 'CG'):
        result = minimize(self.objective_function, initial_params, method=method, options = {'disp': True}, callback=self.logger)
        return result


        