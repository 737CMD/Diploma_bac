import ansys.fluent.core as pyfluent
import subprocess
import json
import os
import numpy as np

# Определяем пути
script_dir = os.path.dirname(os.path.abspath(__file__))
fluent_case_path = os.path.join(script_dir, "optimization_setup.cas.h5")

# --- ВСЕ НАСТРОЙКИ ЗАДАЮТСЯ ЗДЕСЬ ---
config = {
    "Mach": 0.75,
    "Re": 6500000,
    "T": 300,
    "min_thick": 12,
    "target_cl": 0.5,
    "min_r_forw": 0.007, #верхняя граница в 10 раз больше 
    "points": 3,
    "dy_te": 0.00,
    "cl_tol": 0.001,
    "cd_tol": 0.0001,
    "conv_iter": 30,
    "point_bound": 0.2, #макс координата точки
    "teta_bound": np.deg2rad(20) #Максимальный угол заклинения 
}

def main():
    
    # Формируем общий пакет данных для Worker'а
    shared_data = {
        "config": config #Хвост от того, что раньше передавалось больше
    }
    
    #JSON
    json_file = os.path.join(script_dir, 'shared_data.json')
    with open(json_file, 'w') as f:
        json.dump(shared_data, f, indent=4)
        
    print(f"Конфигурация сохранена в {json_file}")
    
    # Запускаем DAKOTA
    print("Запуск DAKOTA...")
    dakota_file_name = "dakota.in"
    try:
        subprocess.run(["dakota", "-i", dakota_file_name, "-o", "dakota.out", "-r", "restart_data.rst"], check=True)
        # "-r", "restart_data.rst" 
    except Exception as e:
        print(f"Критическая ошибка при запуске DAKOTA: {e}")
    finally:
        print("Закрытие сессии Fluent и очистка временных файлов...")
        if os.path.exists(json_file):
            os.remove(json_file)

if __name__ == "__main__":
    main()