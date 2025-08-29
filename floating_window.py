from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

class FloatingPlotWindow(QMainWindow):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setDockOptions(QMainWindow.AllowTabbedDocks | QMainWindow.AllowNestedDocks)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setup_menu()

    def setup_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("Файл")
        
        new_plot_action = QAction("Новый график", self)
        # При вызове из этого окна, цель - это окно
        new_plot_action.triggered.connect(lambda: self.parent().create_new_plot_view(self))
        file_menu.addAction(new_plot_action)

    def closeEvent(self, event):
        # Уведомляем родителя (главное окно) о закрытии
        if self.parent() and hasattr(self.parent(), 'on_floating_window_closed'):
            self.parent().on_floating_window_closed(self)
        super().closeEvent(event)
