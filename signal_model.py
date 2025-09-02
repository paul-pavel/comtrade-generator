from __future__ import annotations
from typing import Dict, Any
import signal_generator
from PySide6.QtCore import QObject, Signal as QtSignal

PLOT_COLORS: list[tuple[int, int, int]] = [
    (255, 0, 0),       # red
    (255, 255, 0),     # yellow
    (0, 255, 0),       # green
    (0, 255, 255),     # cyan
    (255, 0, 255),     # magenta
    (0, 0, 255),       # blue
    (200, 200, 200),   # light gray
    (128, 128, 128)    # gray
]

color_index: int = 0

class Signal(QObject):
    """Класс для представления одного аналогового сигнала."""
    updated: QtSignal = QtSignal()

    def __init__(self, params: Dict[str, Any], equation: str) -> None:
        super().__init__()
        global color_index
        self.params: Dict[str, Any] = params
        self.equation: str = equation
        self.plot_item = None
        self.t = None
        self.y = None
        self.color: tuple[int, int, int] = PLOT_COLORS[color_index % len(PLOT_COLORS)]
        color_index += 1
        self.generate_data()

    def generate_data(self) -> None:
        """Генерирует данные временного ряда (t, y) для сигнала."""
        self.t, self.y = signal_generator.generate_signal_data(self.params, self.equation)

    def update(self, params: Dict[str, Any], equation: str) -> None:
        """Обновляет параметры и уравнение, а затем пересчитывает данные."""
        self.params = params
        self.equation = equation
        self.generate_data()
        self.updated.emit()

    def set_color(self, color: tuple[int, int, int]) -> None:
        """Устанавливает новый цвет для сигнала."""
        self.color = color
        self.updated.emit()

    @property
    def name(self) -> str:
        """Возвращает имя сигнала из его параметров."""
        return self.params.get("name", "Безымянный")
