from PySide6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, 
                               QCheckBox, QScrollArea)
from PySide6.QtCore import Qt
from functools import partial

from widgets.plot_widget import PlotWidget
from signal_model import Signal

class PlotView(QDockWidget):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.signal_plot_items = {} # {Signal: plot_item}
        self.checkboxes = {} # {Signal: QCheckBox}

        main_dock_widget = QWidget()
        self.setWidget(main_dock_widget)
        layout = QHBoxLayout(main_dock_widget)

        # Левая панель для чекбоксов
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumWidth(250)
        
        self.checkbox_container = QWidget()
        self.checkbox_layout = QVBoxLayout(self.checkbox_container)
        self.checkbox_layout.addStretch()
        
        scroll_area.setWidget(self.checkbox_container)
        layout.addWidget(scroll_area)

        # Правая панель для графика
        self.plot_widget = PlotWidget()
        layout.addWidget(self.plot_widget)

        # Разрешаем все виды стыковки и отсоединение
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)

    def update_signal_list(self, all_signals):
        """Обновляет список чекбоксов на основе общей библиотеки сигналов."""
        # Удаляем чекбоксы для сигналов, которых больше нет в библиотеке
        for signal in list(self.checkboxes.keys()):
            if signal not in all_signals:
                checkbox = self.checkboxes.pop(signal)
                checkbox.setParent(None)
                checkbox.deleteLater()
                if signal in self.signal_plot_items:
                    self.hide_signal(signal)

        # Добавляем чекбоксы для новых сигналов
        for signal in all_signals:
            if signal not in self.checkboxes:
                checkbox = QCheckBox(signal.name)
                checkbox.stateChanged.connect(partial(self._on_checkbox_state_changed, signal))
                self.checkbox_layout.insertWidget(self.checkbox_layout.count() - 1, checkbox)
                self.checkboxes[signal] = checkbox

    def _on_checkbox_state_changed(self, signal, state):
        if state == Qt.CheckState.Checked.value:
            self.display_signal(signal)
        else:
            self.hide_signal(signal)

    def display_signal(self, signal: Signal):
        if signal in self.signal_plot_items:
            return
        
        plot_item = self.plot_widget.add_plot(signal.t, signal.y)
        self.signal_plot_items[signal] = plot_item

    def hide_signal(self, signal: Signal):
        if signal not in self.signal_plot_items:
            return

        plot_item = self.signal_plot_items.pop(signal)
        self.plot_widget.remove_plot(plot_item)

    def update_displayed_signal(self, signal: Signal):
        # Обновляем график, если сигнал на нем отображен
        if signal in self.signal_plot_items:
            plot_item = self.signal_plot_items[signal]
            self.plot_widget.update_plot(plot_item, signal.t, signal.y)
        
        # Обновляем текст чекбокса, если имя изменилось
        if signal in self.checkboxes:
            self.checkboxes[signal].setText(signal.name)
