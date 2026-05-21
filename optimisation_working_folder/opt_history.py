import numpy as np
import matplotlib.pyplot as plt
import os

# Путь к файлу с историей (настраивается)
history_file = 'opt_history.dat'

def plot_optimization_history(filename):
    if not os.path.exists(filename):
        print(f"Файл {filename} не найден. Убедись, что DAKOTA уже начала работу.")
        return

    iterations = []
    objectives = []
    valid_iterations = []
    valid_objectives = []

    # Читаем файл DAKOTA
    with open(filename, 'r') as f:
        # Пропускаем заголовок (первая строка содержит имена переменных)
        header = f.readline()
        
        # Находим индекс колонки с целевой функцией (обычно 'obj_fn')
        col_names = header.split()
        try:
            obj_idx = col_names.index('obj_fn')
        except ValueError:
            print("Внимание: колонка 'obj_fn' не найдена. Ищем последнюю колонку.")
            obj_idx = -1 # По умолчанию берем последнюю, если имя другое

        # Читаем данные
        for i, line in enumerate(f):
            parts = line.split()
            if not parts: continue # Пропуск пустых строк
            
            try:
                # DAKOTA пишет номер итерации в первой колонке (%eval_id)
                iteration = int(parts[0])
                obj_val = float(parts[obj_idx])
                
                iterations.append(iteration)
                objectives.append(obj_val)
                
                # Отдельно сохраняем "хорошие" точки (без штрафа)
                if obj_val < 1500:
                    valid_iterations.append(iteration)
                    valid_objectives.append(obj_val)
                    
            except (ValueError, IndexError):
                continue

    if not iterations:
        print("В файле нет данных для построения графика.")
        return

    # Настройка графика
    plt.figure(figsize=(10, 6))
    
    # Строим все точки (серым цветом, чтобы не отвлекали)
    plt.plot(iterations, objectives, 'o', color='lightgray', markersize=4, label='Все попытки (вкл. штрафы)')
    
    # Строим только физичные профили (синим цветом, с линией тренда)
    if valid_iterations:
        plt.plot(valid_iterations, valid_objectives, 'b-o', linewidth=1.5, markersize=6, label='Физичные профили')
        
        # Находим и выделяем лучшую точку
        best_idx = np.argmin(valid_objectives)
        best_iter = valid_iterations[best_idx]
        best_val = valid_objectives[best_idx]
        plt.plot(best_iter, best_val, 'r*', markersize=15, label=f'Оптимум: {best_val:.1f} (Итерация {best_iter})')

    plt.title('История оптимизации профиля (EGO DAKOTA)', fontsize=14)
    plt.xlabel('Номер итерации', fontsize=12)
    plt.ylabel('Целевая функция (Cxa * 10000)', fontsize=12)
    
    # Ограничиваем ось Y, чтобы огромные штрафы не сплющивали полезный график
    # Если есть хорошие точки, смотрим на их масштаб + небольшой запас сверху
    if valid_objectives:
        max_valid = max(valid_objectives)
        plt.ylim(0, max_valid * 3) 
    else:
        plt.ylim(0, max(objectives) * 1.1)

    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_optimization_history(history_file)