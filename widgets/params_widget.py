import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QDoubleSpinBox, QLineEdit, QPushButton)

class ParamsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.param_spinboxes = {}
        self.load_signal_configs()

        main_layout = QVBoxLayout(self)
        
        # Имя сигнала
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Имя:"))
        self.name_edit = QLineEdit("Новый сигнал")
        name_layout.addWidget(self.name_edit)
        main_layout.addLayout(name_layout)

        # Тип сигнала
        signal_type_layout = QHBoxLayout()
        signal_type_layout.addWidget(QLabel("Тип:"))
        self.signal_type_combo = QComboBox()
        self.signal_type_combo.addItems([config['name'] for config in self.signal_configs])
        self.signal_type_combo.currentIndexChanged.connect(self.update_param_fields)
        signal_type_layout.addWidget(self.signal_type_combo)
        main_layout.addLayout(signal_type_layout)

        # Контейнер для динамических полей
        self.params_container_layout = QVBoxLayout()
        main_layout.addLayout(self.params_container_layout)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить в библиотеку")
        buttons_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Обновить в библиотеке")
        buttons_layout.addWidget(self.update_button)
        main_layout.addLayout(buttons_layout)

        main_layout.addStretch()

        self.update_param_fields()

    def load_signal_configs(self):
        try:
            with open('signal_types.json', 'r', encoding='utf-8') as f:
                self.signal_configs = json.load(f)
        except FileNotFoundError:
            self.signal_configs = []

    def update_param_fields(self):
        # Очистка старых полей
        while self.params_container_layout.count():
            item = self.params_container_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                # Рекурсивно очищаем вложенный layout
                while item.layout().count():
                    child_item = item.layout().takeAt(0)
                    if child_item.widget():
                        child_item.widget().setParent(None)
                item.layout().setParent(None)

        self.param_spinboxes.clear()

        # Создание новых полей
        selected_signal_name = self.signal_type_combo.currentText()
        config = next((c for c in self.signal_configs if c['name'] == selected_signal_name), None)
        
        if not config:
            return

        for param_info in config.get('params', []):
            label = param_info['label']
            key = param_info['key']
            default_value = param_info['default']
            
            layout = QHBoxLayout()
            layout.addWidget(QLabel(label))
            spinner = QDoubleSpinBox()
            spinner.setRange(-10000, 10000)
            spinner.setValue(default_value)
            spinner.setSingleStep(0.1)
            layout.addWidget(spinner)
            
            self.params_container_layout.addLayout(layout)
            self.param_spinboxes[key] = spinner

    def get_params_and_equation(self):
        params = {
            "name": self.name_edit.text(),
            "type": self.signal_type_combo.currentText()
        }
        for key, spinner in self.param_spinboxes.items():
            params[key] = spinner.value()
        
        selected_signal_name = self.signal_type_combo.currentText()
        config = next((c for c in self.signal_configs if c['name'] == selected_signal_name), None)
        equation = config.get('equation', '0') if config else '0'

        return params, equation

    def set_params(self, params):
        self.name_edit.setText(params.get("name", ""))
        self.signal_type_combo.setCurrentText(params.get("type", ""))
        # Обновление полей произойдет через сигнал, но значения нужно выставить после
        self.signal_type_combo.blockSignals(True)
        self.update_param_fields()
        for key, spinner in self.param_spinboxes.items():
            if key in params:
                spinner.setValue(params[key])
        self.signal_type_combo.blockSignals(False)
