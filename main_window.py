from __future__ import annotations

from typing import List
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QDockWidget, QListWidget, QListWidgetItem
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from widgets.params_widget import ParamsWidget
from plot_view import PlotView
from signal_model import Signal
from signal_library import SignalLibrary
from floating_window import FloatingPlotWindow
import json

class MainWindow(QMainWindow):
    def __init__(self) -> None:  # type: ignore[override]
        super().__init__()
        self.setWindowTitle("Генератор сигналов")
        self.signal_library: SignalLibrary = SignalLibrary()
        self.plot_views: List[PlotView] = []
        self.floating_windows: List[FloatingPlotWindow] = []

        self.init_ui()
        self.create_menu()
        self.create_plot_view()

    def init_ui(self) -> None:
        """Инициализация пользовательского интерфейса главного окна."""
        self.setDockOptions(QMainWindow.DockOption.AllowTabbedDocks | QMainWindow.DockOption.AllowNestedDocks)

        # --- Панель параметров (слева) ---
        self.setup_params_dock()

        # --- Библиотека сигналов (слева) ---
        self.setup_library_dock()

        self.resize(1400, 800)

    def create_menu(self) -> None:
        """Создает меню приложения."""
        menu = self.menuBar()
        file_menu = menu.addMenu("Файл")
        
        new_plot_action = QAction("Новый график", self)
        new_plot_action.triggered.connect(lambda: self.create_plot_view())
        file_menu.addAction(new_plot_action)

        new_float_win_action = QAction("Новое плавающее окно", self)
        new_float_win_action.triggered.connect(self.create_floating_window)
        file_menu.addAction(new_float_win_action)

    def create_plot_view(self, target_window: QMainWindow | None = None) -> None:
        """Создает и добавляет новое окно с графиком в указанное окно (или в главное)."""
        plot_view = PlotView(f"График {len(self.plot_views) + 1}", target_window or self, self.signal_library)
        self.plot_views.append(plot_view)
        if target_window is None:
            target_window = self
        target_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, plot_view)

    def setup_params_dock(self) -> None:
        params_dock = QDockWidget("Параметры сигнала", self)
        params_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        
        self.params_widget = ParamsWidget()
        self.params_widget.add_button.clicked.connect(self.add_signal)
        self.params_widget.update_button.clicked.connect(self.update_signal_in_library)
        
        params_dock.setWidget(self.params_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, params_dock)

    def setup_library_dock(self) -> None:
        library_dock = QDockWidget("Библиотека сигналов", self)
        library_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        library_widget = QWidget()
        library_layout = QVBoxLayout(library_widget)

        self.library_list_widget = QListWidget()
        self.library_list_widget.itemClicked.connect(self.load_signal_to_params)
        library_layout.addWidget(self.library_list_widget)

        delete_lib_button = QPushButton("Удалить из библиотеки")
        delete_lib_button.clicked.connect(self.remove_signal)
        library_layout.addWidget(delete_lib_button)

        library_dock.setWidget(library_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, library_dock)

    def create_floating_window(self) -> None:
        count = len(self.floating_windows) + 1
        title = f"Плавающее окно {count}"
        floating_win = FloatingPlotWindow(title, self)
        floating_win.closed.connect(lambda: self.on_floating_window_closed(floating_win))
        self.floating_windows.append(floating_win)
        floating_win.setGeometry(self.geometry().x() + 50, self.geometry().y() + 50, 800, 600)
        floating_win.show()

    def on_floating_window_closed(self, window: FloatingPlotWindow) -> None:
        if window in self.floating_windows:
            self.floating_windows.remove(window)
        for index, window in enumerate(self.floating_windows):
            window.setWindowTitle(f"Плавающее окно {index + 1}")

    def add_signal(self) -> None:
        """Добавляет новый сигнал в библиотеку."""
        params, equation = self.params_widget.get_params_and_equation()
        new_signal = Signal(params, equation)
        self.signal_library.add_signal(new_signal)
        self.library_list_widget.addItem(new_signal.name)

    def update_signal_in_library(self) -> None:
        current_row = self.library_list_widget.currentRow()
        if current_row == -1: return

        signal_to_update = self.signal_library[current_row]
        params, equation = self.params_widget.get_params_and_equation()
        signal_to_update.update(params, equation)

        self.library_list_widget.item(current_row).setText(signal_to_update.name)

        for pv in self.plot_views:
            pv.update_displayed_signal(signal_to_update)

    def remove_signal(self) -> None:
        """Удаляет сигнал из библиотеки и обновляет графики."""
        current_row = self.library_list_widget.currentRow()
        if current_row == -1: return

        signal_to_remove = self.signal_library[current_row]
        self.signal_library.remove_signal(signal_to_remove)
        self.library_list_widget.takeItem(current_row)

    def load_signal_to_params(self, item: QListWidgetItem) -> None:
        row = self.library_list_widget.row(item)
        if row > -1:
            signal = self.signal_library[row]
            self.params_widget.set_params(signal.params)

