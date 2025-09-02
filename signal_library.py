from PySide6.QtCore import QObject, Signal as QtSignal
from signal_model import Signal

class SignalLibrary(QObject):
    """
    Модель, управляющая коллекцией сигналов.
    Инкапсулирует логику добавления, удаления и доступа к сигналам.
    """
    signal_added = QtSignal(Signal)
    signal_removed = QtSignal(Signal)
    
    def __init__(self):
        super().__init__()
        self._signals = []

    def add_signal(self, signal: Signal):
        """Добавляет сигнал в библиотеку и уведомляет подписчиков."""
        self._signals.append(signal)
        self.signal_added.emit(signal)

    def remove_signal(self, signal: Signal):
        """Удаляет сигнал из библиотеки и уведомляет подписчиков."""
        if signal in self._signals:
            self._signals.remove(signal)
            self.signal_removed.emit(signal)

    def get_all_signals(self):
        """Возвращает список всех сигналов."""
        return self._signals

    def __iter__(self):
        """Позволяет итерироваться по сигналам в библиотеке."""
        return iter(self._signals)

    def __getitem__(self, index):
        """Позволяет получать доступ к сигналам по индексу."""
        return self._signals[index]
