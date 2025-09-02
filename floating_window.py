from __future__ import annotations
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QAction

class FloatingPlotWindow(QMainWindow):
    closed = Signal()

    def __init__(self, title: str, parent: Optional[QMainWindow] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setDockOptions(QMainWindow.DockOption.AllowTabbedDocks | QMainWindow.DockOption.AllowNestedDocks)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setup_menu()

    def setup_menu(self) -> None:
        menu = self.menuBar()
        file_menu = menu.addMenu("Файл")
        
        new_plot_action = QAction("Новый график", self)
        # При вызове из этого окна, цель - это окно
        new_plot_action.triggered.connect(lambda: self.parent().create_plot_view(self))
        file_menu.addAction(new_plot_action)

    def closeEvent(self, event) -> None:
        # Уведомляем родителя (главное окно) о закрытии через сигнал closed
        self.closed.emit()
        super().closeEvent(event)
