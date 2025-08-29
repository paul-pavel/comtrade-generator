import numpy as np
from asteval import Interpreter

def generate_signal_data(params, equation, duration=2.0, sampling_rate=4000):
    """Генерирует временной ряд и значения сигнала, используя уравнение."""
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    
    # Создаем безопасный интерпретатор
    aeval = Interpreter()
    
    # Добавляем numpy и временной ряд в контекст
    aeval.symtable['numpy'] = np
    aeval.symtable['time'] = t
    
    # Добавляем все параметры из GUI в контекст
    for key, value in params.items():
        aeval.symtable[key] = value

    # Специальная обработка фазы: конвертируем градусы в радианы
    if 'phase' in aeval.symtable:
        aeval.symtable['phase_rad'] = np.deg2rad(aeval.symtable['phase'])

    # Вычисляем уравнение
    try:
        y = aeval.eval(equation)
        # Проверка, что результат является массивом numpy
        if not isinstance(y, (np.ndarray, int, float)):
             raise ValueError("Результат уравнения имеет неверный тип")
    except Exception as e:
        print(f"Ошибка при вычислении уравнения: {e}")
        y = np.zeros_like(t) # Возвращаем нулевой сигнал в случае ошибки
        
    return t, y
