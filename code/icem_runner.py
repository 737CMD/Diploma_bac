import subprocess
import os

def run_icem(icem_exe, rpl_path):
    """
    Запускает RPL скрипт в ICEM.
    Возвращает True при успехе, печатает ошибку только при сбое.
    """
    if not os.path.exists(rpl_path):
        print(f"[Err] Скрипт не найден: {rpl_path}")
        return False
    working_dir = os.path.dirname(rpl_path)
    cmd = [icem_exe, "-batch", "-script", rpl_path]

    try:
        result = subprocess.run(cmd, cwd = working_dir, shell=True, capture_output=True, text=True)        
        if result.returncode != 0:
            print(f"[Fail] Ошибка ICEM в {os.path.basename(rpl_path)}:\n{result.stderr}")
            return False            
        return True

    except Exception as e:
        print(f"[Exception] Критическая ошибка запуска: {e}")
        return False


ICEM_BIN = r"E:\Program files\ANSYS Inc\v242\icemcfd\win64_amd\bin\icemcfd.bat"
SCRIPT = r"E:\tsagi_dipl\Diploma_bac\optimisation_working_folder\airfoil_mesh_script.rpl"
if run_icem(ICEM_BIN, SCRIPT):
    print("Скрипт выполнен успешно.")