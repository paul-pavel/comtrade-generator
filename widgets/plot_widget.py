from __future__ import annotations

from typing import Sequence, Tuple
import numpy as np
from numpy.typing import ArrayLike
import pyqtgraph as pg

ColorTuple = Tuple[int, int, int]


class PlotWidget(pg.PlotWidget):
    def __init__(self, parent=None) -> None:  # type: ignore[override]
        super().__init__(parent)
        self.showGrid(x=True, y=True)
        self.setLabel('left', 'Амплитуда')
        self.setLabel('bottom', 'Время', units='с')

    def add_plot(
        self,
        t: ArrayLike,
        y: ArrayLike,
        color: ColorTuple = (255, 255, 255)
    ) -> pg.PlotDataItem:
        pen = pg.mkPen(color=color, width=2)
        return self.plot(t, y, pen=pen)  # type: ignore[return-value]

    def update_plot(self, plot_item: pg.PlotDataItem, t: ArrayLike, y: ArrayLike) -> None:
        plot_item.setData(t, y)

    def remove_plot(self, plot_item: pg.PlotDataItem) -> None:
        self.removeItem(plot_item)
