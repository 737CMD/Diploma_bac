import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator

def plot_convergence(filename):
    # Получаем текущую директорию скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Формируем полный путь к файлу
    file_path = os.path.join(script_dir, filename)
    
    # Проверяем существование файла
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл '{filename}' не найден в директории скрипта: {script_dir}")
        return
    
    # Чтение данных из файла
    iterations = []
    cya = []
    cxa = []
    mz = []
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        # Пропускаем заголовочные строки
        start_index = 0
        for i, line in enumerate(lines):
            if line.strip() and line.split()[0].isdigit():
                start_index = i
                break
        
        # Считываем данные
        for line in lines[start_index:]:
            parts = line.split()
            if len(parts) >= 4:
                iterations.append(int(parts[0]))
                cya.append(float(parts[1]))
                cxa.append(float(parts[2]))
                mz.append(float(parts[3]))
    
    # Находим максимальный номер итерации
    max_iteration = max(iterations)
    
    # Определяем диапазон последних 2000 итераций по номерам
    start_iteration = max_iteration - 2000
    
    # Фильтруем данные, оставляя только последние 2000 итераций по номеру
    filtered_indices = [i for i, iter_num in enumerate(iterations) if iter_num >= start_iteration]
    
    filtered_iterations = [iterations[i] for i in filtered_indices]
    filtered_cya = [cya[i] for i in filtered_indices]
    filtered_cxa = [cxa[i] for i in filtered_indices]
    filtered_mz = [mz[i] for i in filtered_indices]
    
    print(f"Отображаются итерации с {filtered_iterations[0]} по {filtered_iterations[-1]} "
          f"(всего {len(filtered_iterations)} записей)")
    
    # Вычисляем средние значения за последние 50 итераций по номеру
    last_50_iterations = []
    last_50_cya = []
    last_50_cxa = []
    last_50_mz = []
    
    # Находим индексы последних 50 итераций
    for i in range(len(filtered_iterations)-1, -1, -1):
        if len(last_50_iterations) >= 50:
            break
        last_50_iterations.append(filtered_iterations[i])
        last_50_cya.append(filtered_cya[i])
        last_50_cxa.append(filtered_cxa[i])
        last_50_mz.append(filtered_mz[i])
    
    # Переворачиваем, чтобы были в правильном порядке
    last_50_iterations.reverse()
    last_50_cya.reverse()
    last_50_cxa.reverse()
    last_50_mz.reverse()
    
    avg_cya = np.mean(last_50_cya)
    avg_cxa = np.mean(last_50_cxa)
    avg_mz = np.mean(last_50_mz)
    
    # Вывод средних значений в консоль
    print(f"Среднее значение Cya за последние 50 итераций (с {last_50_iterations[0]} по {last_50_iterations[-1]}): {avg_cya:.6f}")
    print(f"Среднее значение Cxa за последние 50 итераций (с {last_50_iterations[0]} по {last_50_iterations[-1]}): {avg_cxa:.6f}")
    print(f"Среднее значение Mz за последние 50 итераций (с {last_50_iterations[0]} по {last_50_iterations[-1]}): {avg_mz:.6f}")
    
    # Создаем графики
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Функция для установки минимального масштаба 0.001 и настройки сетки
    def set_min_scale_and_grid(ax, data, avg_value):
        y_min = min(data)
        y_max = max(data)
        y_range = y_max - y_min
        
        # Если диапазон данных меньше 0.001, устанавливаем минимальный масштаб 0.001
        if y_range < 0.001:
            half_range = 0.0005
            ax.set_ylim(avg_value - half_range, avg_value + half_range)
        
        # Устанавливаем основные деления сетки с шагом 0.001
        ax.yaxis.set_major_locator(MultipleLocator(0.0001))
        # Устанавливаем дополнительные деления сетки с шагом 0.0005
        ax.yaxis.set_minor_locator(MultipleLocator(0.0005))
    
    # График для Cya
    ax1.plot(filtered_iterations, filtered_cya, 'b-', linewidth=1, label='Cya')
    ax1.axhline(y=avg_cya, color='r', linestyle='--', linewidth=1, 
                label=f'Среднее Cya: {avg_cya:.6f}')
    ax1.set_ylabel('Cya')
    ax1.set_title(f'Сходимость Cya за последние 2000 итераций (с {filtered_iterations[0]} по {filtered_iterations[-1]})')
    ax1.legend(loc='best')
    
    # Настраиваем сетку для Cya
    set_min_scale_and_grid(ax1, filtered_cya, avg_cya)
    ax1.grid(True, which='major', linestyle='-', linewidth=0.5)
    ax1.grid(True, which='minor', linestyle=':', linewidth=0.2)
    
    # График для Cxa
    ax2.plot(filtered_iterations, filtered_cxa, 'g-', linewidth=1, label='Cxa')
    ax2.axhline(y=avg_cxa, color='r', linestyle='--', linewidth=1, 
                label=f'Среднее Cxa: {avg_cxa:.6f}')
    ax2.set_xlabel('Номер итерации')
    ax2.set_ylabel('Cxa')
    ax2.set_title(f'Сходимость Cxa за последние 2000 итераций (с {filtered_iterations[0]} по {filtered_iterations[-1]})')
    ax2.legend(loc='best')
    
    # Настраиваем сетку для Cxa
    set_min_scale_and_grid(ax2, filtered_cxa, avg_cxa)
    ax2.grid(True, which='major', linestyle='-', linewidth=0.5)
    ax2.grid(True, which='minor', linestyle=':', linewidth=0.2)
    
    plt.tight_layout()
    
    # Сохраняем график в текущей директории
    output_filename = os.path.splitext(filename)[0] + '_convergence_plot.png'
    output_path = os.path.join(script_dir, output_filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"График сохранен как: {output_path}")
    
    plt.show()

# Пример использования
plot_convergence("2.83deg-report.out")