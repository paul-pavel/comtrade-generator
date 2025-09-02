from PySide6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, 
                               QCheckBox, QScrollArea, QPushButton, QColorDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from functools import partial
import pyqtgraph as pg

from widgets.plot_widget import PlotWidget
from signal_model import Signal

class PlotView(QDockWidget):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.signal_plot_items = {} # {Signal: plot_item}
        self.checkboxes = {} # {Signal: QCheckBox}
        self.color_buttons = {} # {Signal: QPushButton}
        self.signal_connections = {} # {Signal: connection}

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
        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)

    def update_signal_list(self, all_signals):
        """Обновляет список чекбоксов на основе общей библиотеки сигналов."""
        # Удаляем чекбоксы для сигналов, которых больше нет в библиотеке
        for signal in list(self.checkboxes.keys()):
            if signal not in all_signals:
                # Отключаемся от сигнала
                if signal in self.signal_connections:
                    try:
                        signal.updated.disconnect(self.signal_connections.pop(signal))
                    except (RuntimeError, TypeError):
                        # Соединение могло быть уже удалено или иметь неверный тип
                        pass

                # Удаляем виджет-контейнер
                container_widget = self.checkboxes[signal].parentWidget()
                container_widget.setParent(None)
                container_widget.deleteLater()

                self.checkboxes.pop(signal)
                self.color_buttons.pop(signal)

                if signal in self.signal_plot_items:
                    self.hide_signal(signal)

        # Добавляем чекбоксы для новых сигналов
        for signal in all_signals:
            if signal not in self.checkboxes:
                container = QWidget()
                layout = QHBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)

                checkbox = QCheckBox(signal.name)
                checkbox.stateChanged.connect(partial(self._on_checkbox_state_changed, signal))
                
                color_button = QPushButton()
                color_button.setFixedSize(24, 24)
                color_button.setStyleSheet(f"background-color: rgb{signal.color}; border: 1px solid black;")
                color_button.clicked.connect(partial(self._on_color_button_clicked, signal))

                layout.addWidget(checkbox)
                layout.addWidget(color_button)
                
                self.checkbox_layout.insertWidget(self.checkbox_layout.count() - 1, container)
                self.checkboxes[signal] = checkbox
                self.color_buttons[signal] = color_button

                # Подключаемся к сигналу updated
                connection = partial(self.update_displayed_signal, signal)
                signal.updated.connect(connection)
                self.signal_connections[signal] = connection

    def _on_checkbox_state_changed(self, signal, state):
        if state == Qt.CheckState.Checked.value:
            self.display_signal(signal)
        else:
            self.hide_signal(signal)

    def _on_color_button_clicked(self, signal):
        current_color = QColor(*signal.color)
        color = QColorDialog.getColor(current_color, self, "Выберите цвет")

        if color.isValid():
            signal.set_color((color.red(), color.green(), color.blue()))

    def display_signal(self, signal: Signal):
        if signal in self.signal_plot_items:
            return
        
        plot_item = self.plot_widget.add_plot(signal.t, signal.y, signal.color)
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
            plot_item.setPen(pg.mkPen(color=signal.color, width=2))
        
        # Обновляем текст чекбокса, если имя изменилось
        if signal in self.checkboxes:
            self.checkboxes[signal].setText(signal.name)
            # Обновляем цвет кнопки
            button = self.color_buttons.get(signal)
            if button:
                button.setStyleSheet(f"background-color: rgb{signal.color}; border: 1px solid black;")
