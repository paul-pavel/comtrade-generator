from __future__ import annotations

from typing import Any, Dict, Tuple
import numpy as np
from numpy.typing import NDArray
from asteval import Interpreter


def generate_signal_data(
    params: Dict[str, Any],
    equation: str,
    duration: float = 2.0,
    sampling_rate: int = 4000,
) -> Tuple[NDArray[np.floating], NDArray[np.floating]]:
    """Генерирует временной ряд и значения сигнала, используя уравнение.

    Всегда возвращает массивы numpy одинаковой длины.
    """
    t: NDArray[np.floating] = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

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
        y_obj = aeval.eval(equation)
        if not isinstance(y_obj, (np.ndarray, int, float)):
            raise ValueError("Результат уравнения имеет неверный тип")
        y_arr: NDArray[np.floating] = np.asarray(y_obj, dtype=float)
        if y_arr.shape != t.shape:
            # Пытаемся broadcast / привести к нужной длине
            try:
                y_arr = np.broadcast_to(y_arr, t.shape).astype(float, copy=False)
            except ValueError:
                raise ValueError("Размер результата уравнения не соответствует размеру времени")
    except Exception as e:  # noqa: BLE001 - хотим показывать любые ошибки расчёта
        print(f"Ошибка при вычислении уравнения: {e}")
        y_arr = np.zeros_like(t, dtype=float)

    return t, y_arr
