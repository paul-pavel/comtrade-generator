import signal_generator

class Signal:
    """Класс для представления одного аналогового сигнала."""
    def __init__(self, params, equation):
        self.params = params
        self.equation = equation
        self.plot_item = None
        self.t = None
        self.y = None
        self.generate_data()

    def generate_data(self):
        """Генерирует данные временного ряда (t, y) для сигнала."""
        self.t, self.y = signal_generator.generate_signal_data(self.params, self.equation)

    def update(self, params, equation):
        """Обновляет параметры и уравнение, а затем пересчитывает данные."""
        self.params = params
        self.equation = equation
        self.generate_data()

    @property
    def name(self):
        """Возвращает имя сигнала из его параметров."""
        return self.params.get("name", "Безымянный")
