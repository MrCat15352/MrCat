import re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class InvestigationDialog(QDialog):
    def __init__(self, log_data, parent=None):
        super().__init__(parent)
        self.log_data = log_data
        self.setWindowTitle("🔍 Расследование")
        self.setGeometry(200, 200, 800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Параметры поиска
        params_layout = QVBoxLayout()
        
        # Первая строка - CKey, имя персонажа и радиус
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("CKey цели:"))
        self.ckey_edit = QLineEdit()
        self.ckey_edit.setPlaceholderText("Введите CKey игрока")
        row1.addWidget(self.ckey_edit)
        
        row1.addWidget(QLabel("или имя:"))
        self.character_edit = QLineEdit()
        self.character_edit.setPlaceholderText("Имя персонажа")
        row1.addWidget(self.character_edit)
        
        row1.addWidget(QLabel("Радиус:"))
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 100)
        self.radius_spin.setValue(5)
        row1.addWidget(self.radius_spin)
        
        params_layout.addLayout(row1)
        
        # Вторая строка - координаты
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Координаты цели:"))
        
        row2.addWidget(QLabel("X:"))
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 999)
        self.x_spin.setValue(0)
        row2.addWidget(self.x_spin)
        
        row2.addWidget(QLabel("Y:"))
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 999)
        self.y_spin.setValue(0)
        row2.addWidget(self.y_spin)
        
        row2.addWidget(QLabel("Z:"))
        self.z_spin = QSpinBox()
        self.z_spin.setRange(1, 20)
        self.z_spin.setValue(1)
        row2.addWidget(self.z_spin)
        
        row2.addStretch()
        
        params_layout.addLayout(row2)
        
        # Кнопка поиска
        search_layout = QHBoxLayout()
        self.search_btn = QPushButton("🔍 Найти")
        self.search_btn.clicked.connect(self.perform_investigation)
        search_layout.addWidget(self.search_btn)
        search_layout.addStretch()
        
        params_layout.addLayout(search_layout)
        layout.addLayout(params_layout)
        
        # Фильтры по типам
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Типы:"))
        
        self.colors = {
            'ACCESS': '#4CAF50', 'GAME': '#2196F3', 'EMOTE': '#FF9800',
            'SAY': '#9C27B0', 'ADMIN': '#F44336', 'ERROR': '#FF0000'
        }
        
        self.filter_checkboxes = {}
        for event_type, color in self.colors.items():
            cb = QCheckBox(event_type)
            cb.setChecked(True)
            cb.setStyleSheet(f"QCheckBox {{ color: {color}; font-weight: bold; }}")
            cb.stateChanged.connect(self.apply_type_filter)
            self.filter_checkboxes[event_type] = cb
            filter_layout.addWidget(cb)
        
        colors_btn = QPushButton("Настроить цвета")
        colors_btn.clicked.connect(self.configure_colors)
        filter_layout.addWidget(colors_btn)
        
        layout.addLayout(filter_layout)
        
        # Результаты
        self.results_table = QTableWidget()
        self.results_table.setFont(QFont("Consolas", 9))
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setSortingEnabled(True)
        
        # Контекстное меню для заголовков колонок
        header = self.results_table.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.show_column_menu)
        
        layout.addWidget(self.results_table)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton("💾 Экспорт")
        export_btn.clicked.connect(self.export_results)
        buttons_layout.addWidget(export_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def perform_investigation(self):
        target_ckey = self.ckey_edit.text().strip()
        radius = self.radius_spin.value()
        target_x = self.x_spin.value()
        target_y = self.y_spin.value()
        target_z = self.z_spin.value()
        
        target_character = self.character_edit.text().strip()
        
        if not target_ckey and not target_character:
            QMessageBox.warning(self, "Ошибка", "Введите CKey или имя персонажа")
            return
        
        # Используем указанные координаты как центр поиска
        target_coords = [(None, (target_x, target_y, target_z))]
        
        # Находим все логи в радиусе от цели
        related_logs = self.find_related_logs(target_coords, radius)
        
        # Группируем по Z-уровню
        grouped_logs = self.group_by_z_level(related_logs)
        
        # Отображаем результаты
        target_info = target_ckey if target_ckey else target_character
        search_info = f"{target_info} вокруг ({target_x}, {target_y}, {target_z})"
        self.last_results = (search_info, radius, grouped_logs)
        self.display_results(search_info, radius, grouped_logs)
    
    def extract_coordinates(self, message):
        # Ищем координаты в формате (x, y, z)
        coord_pattern = r'\((\d+),\s*(\d+),\s*(\d+)\)'
        match = re.search(coord_pattern, message)
        if match:
            return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        return None
    
    def find_related_logs(self, target_coords_list, radius):
        related = []
        seen_entries = set()
        
        for target_entry, target_coords in target_coords_list:
            tx, ty, tz = target_coords
            
            for entry in self.log_data:
                entry_id = (entry['line_num'], entry['timestamp'])
                if entry_id in seen_entries:
                    continue
                    
                coords = self.extract_coordinates(entry['message'])
                if coords:
                    x, y, z = coords
                    
                    # Проверяем только один Z-уровень
                    if z == tz:
                        # Вычисляем расстояние
                        distance = ((x - tx) ** 2 + (y - ty) ** 2) ** 0.5
                        if distance <= radius:
                            related.append((entry, coords, distance))
                            seen_entries.add(entry_id)
        
        return related
    
    def group_by_z_level(self, related_logs):
        groups = {}
        for entry, coords, distance in related_logs:
            z = coords[2]
            if z not in groups:
                groups[z] = []
            groups[z].append((entry, coords, distance))
        
        # Сортируем по времени в каждой группе
        for z in groups:
            groups[z].sort(key=lambda x: x[0]['timestamp'])
        
        return groups
    
    def display_results(self, search_info, radius, grouped_logs):
        if not grouped_logs:
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return
        
        # Фильтруем события по типам
        all_events = []
        for z_level, events in grouped_logs.items():
            for entry, coords, distance in events:
                if self.filter_checkboxes.get(entry['type'], QCheckBox()).isChecked():
                    all_events.append((entry, coords, distance, z_level))
        
        # Настраиваем таблицу
        columns = ['Время', 'Тип', 'X', 'Y', 'Z', 'Расст.', 'Сообщение']
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        self.results_table.setRowCount(len(all_events))
        
        # Заполняем данными
        for row, (entry, coords, distance, z_level) in enumerate(all_events):
            x, y, z = coords
            color = QColor(self.colors.get(entry['type'], '#000000'))
            
            items = [
                QTableWidgetItem(entry['timestamp']),
                QTableWidgetItem(entry['type']),
                QTableWidgetItem(str(x)),
                QTableWidgetItem(str(y)),
                QTableWidgetItem(str(z)),
                QTableWidgetItem(str(int(distance))),
                QTableWidgetItem(entry['message'])
            ]
            
            for col, item in enumerate(items):
                if col == 1:  # Колонка типа
                    item.setForeground(color)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.results_table.setItem(row, col, item)
        
        # Автоподбор ширины колонок
        self.results_table.resizeColumnsToContents()
    
    def apply_type_filter(self):
        # Перерисовываем результаты с учетом фильтров
        if hasattr(self, 'last_results'):
            search_info, radius, grouped_logs = self.last_results
            self.display_results(search_info, radius, grouped_logs)
    
    def configure_colors(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройка цветов")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        
        for event_type, color in self.colors.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(event_type))
            
            color_btn = QPushButton()
            color_btn.setStyleSheet(f"background-color: {color}")
            color_btn.clicked.connect(lambda checked, et=event_type: self.change_event_color(et))
            row.addWidget(color_btn)
            
            layout.addLayout(row)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            self.apply_type_filter()
    
    def change_event_color(self, event_type):
        color = QColorDialog.getColor(QColor(self.colors[event_type]), self)
        if color.isValid():
            self.colors[event_type] = color.name()
            self.filter_checkboxes[event_type].setStyleSheet(
                f"QCheckBox {{ color: {color.name()}; font-weight: bold; }}"
            )
    
    def show_column_menu(self, position):
        menu = QMenu(self)
        
        for col in range(self.results_table.columnCount()):
            header_text = self.results_table.horizontalHeaderItem(col).text()
            action = QAction(header_text, self)
            action.setCheckable(True)
            action.setChecked(not self.results_table.isColumnHidden(col))
            action.triggered.connect(lambda checked, c=col: self.toggle_column(c, checked))
            menu.addAction(action)
        
        menu.exec_(self.results_table.horizontalHeader().mapToGlobal(position))
    
    def toggle_column(self, column, visible):
        if visible:
            self.results_table.showColumn(column)
        else:
            self.results_table.hideColumn(column)
    
    def export_results(self):
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Нет результатов для экспорта")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить результаты расследования", "", "CSV files (*.csv);;All files (*.*)"
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                import csv
                writer = csv.writer(f)
                
                # Заголовки
                headers = []
                for col in range(self.results_table.columnCount()):
                    if not self.results_table.isColumnHidden(col):
                        headers.append(self.results_table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Данные
                for row in range(self.results_table.rowCount()):
                    row_data = []
                    for col in range(self.results_table.columnCount()):
                        if not self.results_table.isColumnHidden(col):
                            item = self.results_table.item(row, col)
                            row_data.append(item.text() if item else '')
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "Успех", f"Результаты сохранены: {file_path}")