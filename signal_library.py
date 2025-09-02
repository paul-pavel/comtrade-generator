from __future__ import annotations

from typing import List, Iterator
from PySide6.QtCore import QObject, Signal as QtSignal
from signal_model import Signal

class SignalLibrary(QObject):
    """
    Модель, управляющая коллекцией сигналов.
    Инкапсулирует логику добавления, удаления и доступа к сигналам.
    """
    signal_added = QtSignal(Signal)
    signal_removed = QtSignal(Signal)
    
    def __init__(self) -> None:
        super().__init__()
        self._signals: List[Signal] = []

    def add_signal(self, signal: Signal) -> None:
        """Добавляет сигнал в библиотеку и уведомляет подписчиков."""
        self._signals.append(signal)
        self.signal_added.emit(signal)

    def remove_signal(self, signal: Signal) -> None:
        """Удаляет сигнал из библиотеки и уведомляет подписчиков."""
        if signal in self._signals:
            self._signals.remove(signal)
            self.signal_removed.emit(signal)

    def get_all_signals(self) -> List[Signal]:
        """Возвращает список всех сигналов (мутируемый)."""
        return self._signals

    def __iter__(self) -> Iterator[Signal]:
        """Позволяет итерироваться по сигналам в библиотеке."""
        return iter(self._signals)

    def __getitem__(self, index: int) -> Signal:
        """Позволяет получать доступ к сигналам по индексу."""
        return self._signals[index]
