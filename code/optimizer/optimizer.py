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
target_cl = 0.3 #целевое значение Cl
min_r_forw = 0.007 #минимальный радиус кривизны передней кромки
points = 3 #количество точек на верхней и нижней поверхностях профиля (без учета точек передней и задней кромок)
dy_te = 0.0 #зазор в задней кромке
teta = 2 #Угол задней кромки в  градусах
teta = np.deg2rad(teta)

#Настройки расчета
solver = 'density' #выбор солвера: 'pressure' или 'density'
cl_tol = 0.002 #допустимое отклонение Cl от целевого значения при расчете Cd и требование по сходимости
cd_tol = 0.0001 #Ширина полосы допустимых для сходимости cx (рекомендуется оставить 1 count
conv_iter = 30 #Длина полосы, в которой проводится проверка сходимости


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
        self.tg_count = 0
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

    def objective_function(self, params):
        self.tf_count += 1
        self.fine_function = 0
        airfoil = self.create_airfoil_from_params(params)
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
        objective_value = (np.round(cd*10000, 4) + 10*self.fine_function**2)
        print(f"Вызов целевой номер {self.tf_count}, Cya = {cl}, Cxa = {np.round(cd*10000, 4)}, K = {cl/cd}, object = {objective_value}")
        return objective_value
    
    def optimize(self, initial_params, method = 'CG'):
        self.tf_count = 0
        self.params_history = np.array([initial_params])
        self.solver = pyfluent.launch_fluent(processor_count= 10, dimension = 2, cwd = script_dir, precision= "double", case_file_name = fluent_case_path,
                                        show_gui= True, start_transcript = False)
        result = minimize(self.objective_function, initial_params, method=method, options = {'disp': True, 'eps': 1e-2}, callback=self.logger)
        return result

start_time = time.time()
optim = optimizer()
caca0012 = airfoil_generator.airfoil_structured(0.013, [0.1, 0.03], [-0.06], teta, dy_te = 0, min_thick= min_thick)
print(f'Начальные ограничения: Число Маха = {Mach}, Re = {Re}, T = {T}K, min thickness = {min_thick}%, target Cl = {target_cl}, \n min r_forw = {min_r_forw} chord, points = {points}, dy_te = {dy_te}, teta = {np.rad2deg(teta)} degrees')
for i in range(points - 2):
    caca0012.elevate()
caca0012.plot()
params = [caca0012.r_forw*100] + list(caca0012.up_y_coords[2:-1]*10) + list(caca0012.down_y_coords[2:-2]*10)
#params = [ 1.34705691,  0.85044635,  0.55575527,  0.28463824, -0.4402194,  -0.12867087]
print(optim.optimize(params, method = 'CG'))
finish_time = time.time()
print(f"Оптимизация заняла {(finish_time-start_time)/60/60} часов")



        