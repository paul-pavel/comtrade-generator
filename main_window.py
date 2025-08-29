from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QPushButton, QDockWidget, QListWidget)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from widgets.params_widget import ParamsWidget
from plot_view import PlotView
from signal_model import Signal
from floating_window import FloatingPlotWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Генератор сигналов")
        self.signals = [] # Центральная библиотека сигналов
        self.plot_views = []
        self.plot_counter = 0
        self.floating_windows = []

        # Включаем расширенные возможности стыковки
        self.setDockOptions(QMainWindow.AllowTabbedDocks | QMainWindow.AllowNestedDocks)

        # --- Панель параметров (слева) ---
        self.setup_params_dock()

        # --- Библиотека сигналов (слева) ---
        self.setup_library_dock()

        # --- Меню ---
        self.setup_main_menu()

        self.create_new_plot_view(self)

        self.resize(1400, 800)

    def setup_main_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("Файл")
        
        new_plot_action = QAction("Новый график", self)
        # При вызове из главного окна, цель - само главное окно
        new_plot_action.triggered.connect(lambda: self.create_new_plot_view(self))
        file_menu.addAction(new_plot_action)

        new_float_win_action = QAction("Новое плавающее окно", self)
        new_float_win_action.triggered.connect(self.create_floating_window)
        file_menu.addAction(new_float_win_action)

    def create_floating_window(self):
        count = len(self.floating_windows) + 1
        title = f"Плавающее окно {count}"
        floating_win = FloatingPlotWindow(title, self)
        self.floating_windows.append(floating_win)
        floating_win.setGeometry(self.geometry().x() + 50, self.geometry().y() + 50, 800, 600)
        floating_win.show()

    def on_floating_window_closed(self, window):
        if window in self.floating_windows:
            self.floating_windows.remove(window)

    def setup_params_dock(self):
        params_dock = QDockWidget("Параметры сигнала", self)
        params_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.params_widget = ParamsWidget()
        self.params_widget.add_button.clicked.connect(self.add_signal_to_library)
        self.params_widget.update_button.clicked.connect(self.update_signal_in_library)
        
        params_dock.setWidget(self.params_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, params_dock)

    def setup_library_dock(self):
        library_dock = QDockWidget("Библиотека сигналов", self)
        library_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        library_widget = QWidget()
        library_layout = QVBoxLayout(library_widget)

        self.library_list_widget = QListWidget()
        self.library_list_widget.itemClicked.connect(self.load_signal_to_params)
        library_layout.addWidget(self.library_list_widget)

        delete_lib_button = QPushButton("Удалить из библиотеки")
        delete_lib_button.clicked.connect(self.remove_signal_from_library)
        library_layout.addWidget(delete_lib_button)

        library_dock.setWidget(library_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, library_dock)

    def create_new_plot_view(self, target_window):
        self.plot_counter += 1
        title = f"График {self.plot_counter}"
        
        plot_view = PlotView(title, target_window)
        
        self.plot_views.append(plot_view)
        target_window.addDockWidget(Qt.RightDockWidgetArea, plot_view)
        
        # Сразу обновляем список доступных сигналов для нового графика
        plot_view.update_signal_list(self.signals)

    def add_signal_to_library(self):
        params, equation = self.params_widget.get_params_and_equation()
        new_signal = Signal(params, equation)
        self.signals.append(new_signal)
        self.library_list_widget.addItem(new_signal.name)
        self._update_all_plot_views()

    def update_signal_in_library(self):
        current_row = self.library_list_widget.currentRow()
        if current_row == -1: return

        signal_to_update = self.signals[current_row]
        params, equation = self.params_widget.get_params_and_equation()
        signal_to_update.update(params, equation)

        self.library_list_widget.item(current_row).setText(signal_to_update.name)

        for pv in self.plot_views:
            pv.update_displayed_signal(signal_to_update)

    def remove_signal_from_library(self):
        current_row = self.library_list_widget.currentRow()
        if current_row == -1: return

        # Перед удалением сигнала из данных, нужно скрыть его со всех графиков
        signal_to_remove = self.signals[current_row]
        for pv in self.plot_views:
            pv.hide_signal(signal_to_remove)

        self.signals.pop(current_row)
        self.library_list_widget.takeItem(current_row)
        
        # Затем обновить списки чекбоксов на всех графиках
        self._update_all_plot_views()

    def load_signal_to_params(self, item):
        row = self.library_list_widget.row(item)
        if row > -1:
            signal = self.signals[row]
            self.params_widget.set_params(signal.params)

    def _update_all_plot_views(self):
        for pv in self.plot_views:
            pv.update_signal_list(self.signals)
