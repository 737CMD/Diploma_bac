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
    "min_r_forw": 0.007,
    "points": 3,
    "dy_te": 0.005,
    "cl_tol": 0.0015,
    "cd_tol": 0.0001,
    "conv_iter": 30,
    "r_bound": 0.07, #макс радиус кривизны передней кромки
    "point_bound": 0.2, #макс координата точки
    "teta_bound": np.deg2rad(20) #Максимальный угол заклинения 
}

def main():
    print("Запуск сессии Fluent как сервера...")
    session = pyfluent.launch_fluent(
        processor_count=10, 
        dimension=2, 
        cwd=script_dir, 
        precision="double", 
        case_file_name=fluent_case_path,
        show_gui=False, 
        start_transcript=False
    )
    
    # Формируем общий пакет данных для Worker'а
    shared_data = {
        "connection": {
            "ip": session.connection_properties.ip,
            "port": session.connection_properties.port,
            "password": session.connection_properties.password
        },
        "config": config
    }
    
    # Сохраняем в единый JSON
    json_file = os.path.join(script_dir, 'shared_data.json')
    with open(json_file, 'w') as f:
        json.dump(shared_data, f, indent=4)
        
    print(f"Fluent готов. Конфигурация и доступы сохранены в {json_file}")
    
    # Запускаем DAKOTA
    print("Запуск DAKOTA...")
    try:
        subprocess.run(["dakota", "-i", "dakota.in", "-o", "dakota.out"], check=True)
    except Exception as e:
        print(f"Критическая ошибка при запуске DAKOTA: {e}")
    finally:
        print("Закрытие сессии Fluent и очистка временных файлов...")
        session.exit()
        if os.path.exists(json_file):
            os.remove(json_file)

if __name__ == "__main__":
    main()