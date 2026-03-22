import numpy as np
import matplotlib.pyplot as plt
import icem_runner as ir
import airfoil_generator
import fluent_runner 
from scipy.optimize import minimize
import ansys.fluent.core as pyfluent
import time
import os

#Условия оптимизации 
Mach = 0.75
Re = 6500000
T = 300 #температура воздуха в Кельвинах

#Требования на профиль
min_thick = 12  #минимальная толщина профиля в процентах от хорды
target_cl = 0.5 #целевое значение Cl
min_r_forw = 0.007 #минимальный радиус кривизны передней кромки
points = 3 #количество точек на верхней и нижней поверхностях профиля (без учета точек передней и задней кромок)
dy_te = 0.005 #зазор в задней кромке

#Настройки расчета
solver = 'density' #выбор солвера: 'pressure' или 'density'
cl_tol = 0.0015 #допустимое отклонение Cl от целевого значения при расчете Cd и требование по сходимости
cd_tol = 0.0001 #Ширина полосы допустимых для сходимости cx (рекомендуется оставить 1 count
conv_iter = 30 #Длина полосы, в которой проводится проверка сходимости

#параметры нормализации для оптимизации
r_bound = 0.07 #максимальный радиус кривизны передней кромки
point_bound = 0.2 #максимальная координата точек по y
teta_bound = 20 #Угол задней кромки в градусах
teta_bound = np.deg2rad(teta_bound)

# Получаем текущую директорию скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))

#Пути к файлам рабочим
icem_exe = r"E:\Program files\ANSYS Inc\v242\icemcfd\win64_amd\bin\icemcfd.bat"
rpl_script_path = os.path.join(script_dir, "airfoil_mesh_script.rpl")
fluent_case_path = os.path.join(script_dir, "optimization_setup.cas.h5")
report_file_name = os.path.join(script_dir, "curropt-report.out")
mesh_file = os.path.join(script_dir, "geom.msh")
try:
    os.remove(report_file_name)
    print('trace-file removed')
except: 
    pass
class optimizer: 
    #Класс-оптимизатор. В нем удобно хранить всякое барахло
    def __init__(self, show_im_afs = False):
        self.show_im_afs = show_im_afs
        self.params_history = np.array([[]])
        self.objective_history = np.array([])
        self.tf_count = 0
        self.iter_counts = 0
        self.fine_function = 0
        
    def create_airfoil_from_params(self, params):
        params = np.array(params)
        r_forw = params[0]/100
        if  r_forw < min_r_forw: 
            self.fine_function += (min_r_forw - r_forw)*1000
        up_coords = params[1:points+1]/10
        down_coords = params[points+1:]/10
        airfoil = airfoil_generator.airfoil_structured(r_forw, up_coords, down_coords, teta, dy_te, min_thick)
        return airfoil
    
    def create_airfoil_from_norm_params(self, params, r_bound, point_bound, teta_bound, points, dy_te, min_thick):
        r_forw = params[0]*r_bound
        if  r_forw < min_r_forw: 
            self.fine_function += (min_r_forw - r_forw)*1000
        up_coords = params[1:points+1]*point_bound
        down_coords = params[points+1:-1]*point_bound
        teta = params[-1]*teta_bound
        airfoil = airfoil_generator.airfoil_structured(r_forw, up_coords, down_coords, teta, dy_te, min_thick)
        return airfoil
    def find_optimal_eps(self, initial_params, param_index=0, eps_min=1e-5, eps_max=1e-1, num_points=10):
        print(f"\n--- АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ EPS (параметр {param_index}) ---")      
        self.solver = pyfluent.launch_fluent(processor_count = 10, dimension = 2, cwd = script_dir, precision= "double", case_file_name = fluent_case_path,
                                        show_gui= True, start_transcript = False)        
        self.tf_count = 0

        print("Вычисление базовой точки f(x0)...")
        f0 = self.objective_function(initial_params)

        # Генерируем логарифмическую сетку для eps (например, от 0.00001 до 0.1)
        eps_array = np.logspace(np.log10(eps_min), np.log10(eps_max), num_points)
        derivatives = []
        valid_eps =[]

        for eps in eps_array:
            print(f"\nТестируем шаг eps = {eps:.2e} ...")
            x_perturbed = np.array(initial_params, dtype=float)
            x_perturbed[param_index] += eps           
            f1 = self.objective_function(x_perturbed)           
            if f1 >= 1000:
                print(f"-> Ошибка солвера/геометрии при eps = {eps:.2e}. Точка пропущена.")
                continue
            df_dx = (f1 - f0) / eps
            derivatives.append(df_dx)
            valid_eps.append(eps)
            print(f"-> Производная: {df_dx:.4f}")

        plt.figure(figsize=(10, 6))
        plt.semilogx(valid_eps, derivatives, marker='o', linestyle='-', linewidth=2, color='b')
        plt.xlabel('Шаг дифференцирования (eps)', fontsize=12)
        plt.ylabel(f'Производная d(Cd*10k)/dx', fontsize=12)
        plt.title('Зависимость значения производной от шага eps', fontsize=14)
        plt.grid(True, which="both", ls="--", alpha=0.7)
        plt.tight_layout()
        plt.show()
        return valid_eps, derivatives    
    
    def logger(self, *, intermediate_result):
        current_params = intermediate_result.x
        current_objective = intermediate_result.fun
        self.params_history = np.append(self.params_history, [current_params], axis=0)
        self.objective_history = np.append(self.objective_history, current_objective)
        self.iter_counts += 1
        print(f"Итерация: {self.iter_counts}, params: {current_params}, objective: {current_objective}")
        if self.show_im_afs:
            airfoil = self.create_airfoil_from_params(current_params)
            airfoil.plot() 
        #стоп-кран для остановки, потому что xtol, gtol может не работать 
        res = 100
        if self.iter_counts >= 10:
            recent_objectives = self.objective_history[-5:]
            res = np.max(recent_objectives) - np.min(recent_objectives)
        if res <= 0.5:
            print("Достигнут предел точности")
            #raise StopIteration

    def objective_function(self, params):        
        self.tf_count += 1
        self.fine_function = 0
        try:
            airfoil = self.create_airfoil_from_norm_params(params, r_bound, point_bound, teta_bound, points, dy_te, min_thick)
            if airfoil.self_intersect():
                print("Профиль самопересекается. Пропуск итерации.")
                return 1000  # штраф за самопересечение
            # Сохранение координат профиля в файл для ICEM
            airfoil.create_icem_file(500)
            # Запуск ICEM для генерации сетки
            mesh_success = ir.run_icem(icem_exe, rpl_script_path)
            if not mesh_success:
                print("Ошибка при генерации сетки в ICEM. Пропуск итерации.")
                return 1000  # штраф за ошибку сетки

            # Запуск Fluent для расчета аэродинамики
            cl, cd = fluent_runner.run_fluent_simulation(self.solver, target_cl, cl_tol, cd_tol, Mach, Re, T, conv_iter, mesh_file, report_file_name)
            if cl is None or cd is None:
                print("Ошибка при расчете в Fluent. Пропуск итерации.")
                return 1000  # штраф за ошибку расчета    
            # Целевая функция: минимизация Cd при достижении целевого Cl
            objective_value = (cd*10000 + 10*self.fine_function**2)
            print(f"Вызов целевой номер {self.tf_count}, Cya = {cl}, Cxa = {np.round(cd*10000, 4)}, K = {cl/cd}, object = {np.round(objective_value, 2)}")
            return objective_value
        except:
            print("Непредвиденная ошибка в целевой функции. Пропуск итерации.")
            print(f"Параметры, вызвавшие ошибку: {params}")
            return 10000  # штраф за любую непредвиденную ошибку
    
    def optimize(self, initial_params, method = 'CG'):
        self.tf_count = 0
        self.params_history = np.array([initial_params])
        self.solver = pyfluent.launch_fluent(processor_count = 10, dimension = 2, cwd = script_dir, precision= "double", case_file_name = fluent_case_path,
                                        show_gui= True, start_transcript = False)
        result = minimize(self.objective_function, initial_params, method=method, options = {'disp': True, 'eps': 5e-3}, callback=self.logger)
        #bounds = [(min_r_forw/r_bound, 1)] + [(-1, 1)]*(points) + [(-1, 1)]*(points-1) + [(0, 1)]
        #result = minimize(self.objective_function, initial_params, method="trust-constr", jac = "BFGS", options = {'verbose': 2, 'finite_diff_rel_step': 5e-3, 
        #                                                                                                        'initial_tr_radius': 0.2,  
        #                                                                                                        'xtol': 1e-3, 'gtol': 1}, bounds = bounds, callback=self.logger)
        return result

start_time = time.time()
optim = optimizer()
print(f'Начальные ограничения: Число Маха = {Mach}, Re = {Re}, T = {T}K, min thickness = {min_thick}%, target Cl = {target_cl}, \n min r_forw = {min_r_forw} chord, points = {points}, dy_te = {dy_te}, teta < {np.rad2deg(teta_bound)} degrees')
#params = np.array([ 0.3 ,  0.4 ,  0.4  , 0.12, -0.4 , -0.4  , 0.5 ])
params = np.array([ 0.2489275,   0.33049491,  0.42309082,  0.24830995, -0.37643979, -0.36847309,
  0.47196079])
optim.create_airfoil_from_norm_params(params, r_bound, point_bound, teta_bound, points, dy_te, min_thick).plot(show_circle=True)
x = optim.optimize(params, method = 'CG')
print(f"Результат оптимизации: {x.x}")
finish_time = time.time()
optimal_af = optim.create_airfoil_from_norm_params(x.x, r_bound, point_bound, teta_bound, points, dy_te, min_thick)
optimal_af.plot(show_circle=True)
print(f"Оптимизация заняла {(finish_time-start_time)/60/60} часов")



        