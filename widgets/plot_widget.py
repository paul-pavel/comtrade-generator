import pyqtgraph as pg
import numpy as np

class PlotWidget(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.showGrid(x=True, y=True)
        self.setLabel('left', 'Амплитуда')
        self.setLabel('bottom', 'Время', units='с')

    def add_plot(self, t, y):
        pen = pg.mkPen(color=(np.random.randint(100, 255), np.random.randint(100, 255), np.random.randint(100, 255)), width=2)
        return self.plot(t, y, pen=pen)

    def update_plot(self, plot_item, t, y):
        plot_item.setData(t, y)

    def remove_plot(self, plot_item):
        self.removeItem(plot_item)
