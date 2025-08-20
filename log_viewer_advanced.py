import sys
import re
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from investigation_dialog import InvestigationDialog

class LogViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shiptest Log Viewer Advanced")
        self.setGeometry(100, 100, 1400, 900)
        
        self.colors = {
            'ACCESS': '#4CAF50', 'GAME': '#2196F3', 'EMOTE': '#FF9800',
            'SAY': '#9C27B0', 'ADMIN': '#F44336', 'ERROR': '#FF0000'
        }
        
        self.table_mode = False
        self.log_data = []
        self.settings_file = 'log_viewer_settings.json'
        self.load_settings()
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Панель инструментов
        toolbar = self.addToolBar("Main")
        
        load_action = QAction("📁 Открыть", self)
        load_action.triggered.connect(self.load_log)
        toolbar.addAction(load_action)
        
        clear_action = QAction("🗑️ Очистить", self)
        clear_action.triggered.connect(self.clear_log)
        toolbar.addAction(clear_action)
        
        toolbar.addSeparator()
        
        zoom_in_action = QAction("🔍+ Увеличить", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("🔍- Уменьшить", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        toolbar.addSeparator()
        
        split_action = QAction("⚏ Разделить", self)
        split_action.triggered.connect(self.toggle_split)
        toolbar.addAction(split_action)
        
        toolbar.addSeparator()
        
        self.table_mode = False
        self.table_action = QAction("📊 Таблица", self)
        self.table_action.triggered.connect(self.toggle_table_mode)
        toolbar.addAction(self.table_action)
        
        toolbar.addSeparator()
        
        investigation_action = QAction("🔍 Расследование", self)
        investigation_action.triggered.connect(self.open_investigation)
        toolbar.addAction(investigation_action)
        
        toolbar.addSeparator()
        
        # Меню оформления
        style_menu = QMenu("🎨 Оформление", self)
        
        colors_action = QAction("🎨 Цвета типов", self)
        colors_action.triggered.connect(self.configure_colors)
        style_menu.addAction(colors_action)
        
        highlight_colors_action = QAction("✨ Цвета подсветки", self)
        highlight_colors_action.triggered.connect(self.configure_highlight_colors)
        style_menu.addAction(highlight_colors_action)
        
        style_menu.addSeparator()
        
        font_action = QAction("🔤 Шрифт", self)
        font_action.triggered.connect(self.configure_font)
        style_menu.addAction(font_action)
        
        style_menu.addSeparator()
        
        theme_action = QAction("🎨 Тема", self)
        theme_action.triggered.connect(self.configure_theme)
        style_menu.addAction(theme_action)
        
        workspace_color_action = QAction("📝 Цвет рабочей области", self)
        workspace_color_action.triggered.connect(self.configure_workspace_color)
        style_menu.addAction(workspace_color_action)
        
        style_button = QToolButton()
        style_button.setText("🎨 Оформление")
        style_button.setMenu(style_menu)
        style_button.setPopupMode(QToolButton.InstantPopup)
        toolbar.addWidget(style_button)
        
        toolbar.addSeparator()
        
        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
        

        
        # Поиск и фильтры
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        search_layout.addWidget(QLabel("🔍 Поиск:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Введите текст для поиска...")
        self.search_edit.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_edit)
        
        self.case_sensitive = QCheckBox("Учитывать регистр")
        self.case_sensitive.stateChanged.connect(self.on_search)
        search_layout.addWidget(self.case_sensitive)
        
        self.regex_search = QCheckBox("Regex")
        self.regex_search.stateChanged.connect(self.on_search)
        search_layout.addWidget(self.regex_search)
        
        regex_help = QPushButton("?")
        regex_help.setMaximumWidth(25)
        regex_help.clicked.connect(self.show_regex_help)
        search_layout.addWidget(regex_help)
        
        layout.addLayout(search_layout)
        
        # Фильтры по типам
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(5)
        filter_layout.addWidget(QLabel("Типы:"))
        
        self.filter_checkboxes = {}
        for event_type, color in self.colors.items():
            cb = QCheckBox(event_type)
            cb.setChecked(True)
            cb.setStyleSheet(f"QCheckBox {{ color: {color}; font-weight: bold; }}")
            cb.stateChanged.connect(self.apply_filters)
            self.filter_checkboxes[event_type] = cb
            filter_layout.addWidget(cb)
        
        filter_layout.addStretch()
        

        
        layout.addLayout(filter_layout)
        
        # Фильтры по дате и ключу
        date_filter_layout = QHBoxLayout()
        date_filter_layout.setSpacing(10)
        
        self.date_filter_enabled = QCheckBox("Фильтр по дате")
        self.date_filter_enabled.stateChanged.connect(self.apply_filters)
        date_filter_layout.addWidget(self.date_filter_enabled)
        
        date_filter_layout.addWidget(QLabel("с:"))
        self.date_from = QDateTimeEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd.MM.yyyy hh:mm:ss")
        self.date_from.setDateTime(QDateTime.currentDateTime().addDays(-1))
        self.date_from.dateTimeChanged.connect(self.apply_filters)
        date_filter_layout.addWidget(self.date_from)
        
        date_filter_layout.addWidget(QLabel("до:"))
        self.date_to = QDateTimeEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd.MM.yyyy hh:mm:ss")
        self.date_to.setDateTime(QDateTime.currentDateTime())
        self.date_to.dateTimeChanged.connect(self.apply_filters)
        date_filter_layout.addWidget(self.date_to)
        
        date_filter_layout.addWidget(QLabel("CKey:"))
        self.key_filter = QLineEdit()
        self.key_filter.setPlaceholderText("Фильтр по CKey (пусто = все)")
        self.key_filter.textChanged.connect(self.apply_filters)
        date_filter_layout.addWidget(self.key_filter)
        
        date_filter_layout.addWidget(QLabel("Режим фильтров:"))
        
        self.filter_mode_group = QButtonGroup()
        self.hide_radio = QRadioButton("Скрыть")
        self.hide_radio.setChecked(True)
        self.dim_radio = QRadioButton("Затемнить")
        
        self.filter_mode_group.addButton(self.hide_radio)
        self.filter_mode_group.addButton(self.dim_radio)
        
        self.hide_radio.toggled.connect(self.apply_filters)
        
        date_filter_layout.addWidget(self.hide_radio)
        date_filter_layout.addWidget(self.dim_radio)
        
        layout.addLayout(date_filter_layout)
        
        # Подсветка строк
        highlight_layout = QHBoxLayout()
        highlight_layout.setSpacing(10)
        highlight_layout.addWidget(QLabel("Подсветка строк:"))
        
        self.highlight_edits = []
        
        for i in range(5):
            edit = QLineEdit()
            edit.setPlaceholderText(f"Текст {i+1}")
            edit.setStyleSheet(f"background-color: {self.highlight_colors[i]}; color: #000;")
            edit.textChanged.connect(self.apply_filters)
            self.highlight_edits.append(edit)
            highlight_layout.addWidget(edit)
        

        
        layout.addLayout(highlight_layout)
        
        # Сплиттер для двух областей просмотра
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Левая область
        self.text_edit1 = QTextEdit()
        self.text_edit1.setFont(self.default_font)
        self.text_edit1.setLineWrapMode(QTextEdit.NoWrap)
        self.text_edit1.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_edit1.customContextMenuRequested.connect(self.show_context_menu)
        
        # Правая область
        self.text_edit2 = QTextEdit()
        self.text_edit2.setFont(self.default_font)
        self.text_edit2.setLineWrapMode(QTextEdit.NoWrap)
        self.text_edit2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_edit2.customContextMenuRequested.connect(self.show_context_menu)
        
        self.splitter.addWidget(self.text_edit1)
        self.splitter.addWidget(self.text_edit2)
        self.splitter.setSizes([700, 700])
        
        # Изначально показываем только одну область
        self.text_edit2.hide()
        
        layout.addWidget(self.splitter)
        
        # Статус бар с постоянным виджетом для статистики
        self.stats_label = QLabel("Готов к загрузке логов")
        self.statusBar().addPermanentWidget(self.stats_label)
        self.statusBar().showMessage("Готов")
        
    def load_log(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите лог файл", "", "Log files (*.log);;All files (*.*)"
        )
        
        if file_path:
            try:
                self.statusBar().showMessage("Загрузка...")
                QApplication.processEvents()
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.parse_log(content)
                self.display_log()
                self.update_stats()
                self.statusBar().showMessage(f"Загружено: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {e}")
                self.statusBar().showMessage("Ошибка загрузки")
    
    def parse_log(self, content):
        self.log_data = []
        pattern = r'\[([^\]]+)\] (\w+): (.+)'
        
        for line_num, line in enumerate(content.split('\n'), 1):
            if line.strip():
                match = re.match(pattern, line)
                if match:
                    timestamp, event_type, message = match.groups()
                    try:
                        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            dt = None
                    
                    self.log_data.append({
                        'line_num': line_num,
                        'timestamp': timestamp,
                        'datetime': dt,
                        'type': event_type,
                        'message': message,
                        'full_line': line
                    })
    
    def display_log(self):
        self.text_edit1.clear()
        self.text_edit2.clear()
        
        if self.table_mode:
            self.display_table_format()
        else:
            self.display_text_format()
        
        self.apply_search_highlight()
    
    def display_text_format(self):
        html_content = "<pre style='font-family: Consolas, monospace; font-size: 10pt;'>"
        
        for entry in self.log_data:
            if not self.should_show_entry(entry):
                continue
            
            line = entry['full_line']
            color = self.colors.get(entry['type'], '#000000')
            opacity = self.get_entry_opacity(entry)
            
            # Проверяем подсветку
            highlight_color = None
            for i, edit in enumerate(self.highlight_edits):
                text = edit.text().strip()
                if text and text.upper() in entry['full_line'].upper():
                    highlight_color = self.highlight_colors[i]
                    break
            
            if highlight_color:
                html_content += f"<div style='background-color: {highlight_color}; color: #000; font-weight: bold;'>{line}</div>"
            else:
                html_content += f"<div style='color: {color}; font-weight: bold;'>{line}</div>"
        
        html_content += "</pre>"
        self.text_edit1.setHtml(html_content)
        self.text_edit2.setHtml(html_content)
    
    def display_table_format(self):
        if not hasattr(self, 'table_widget'):
            self.setup_table_widget()
        
        # Собираем данные для таблицы
        table_data = []
        for entry in self.log_data:
            if not self.should_show_entry(entry):
                continue
            
            parsed = self.parse_message(entry['message'], entry['type'])
            
            # Проверяем подсветку
            highlight_color = None
            for i, edit in enumerate(self.highlight_edits):
                text = edit.text().strip()
                if text and text.upper() in entry['full_line'].upper():
                    highlight_color = self.highlight_colors[i]
                    break
            
            opacity = float(self.get_entry_opacity(entry))
            
            table_data.append({
                'entry': entry,
                'parsed': parsed,
                'highlight_color': highlight_color,
                'opacity': opacity
            })
        
        # Заполняем таблицу
        self.table_widget.setRowCount(len(table_data))
        
        for row, data in enumerate(table_data):
            entry = data['entry']
            parsed = data['parsed']
            highlight_color = data['highlight_color']
            opacity = data['opacity']
            
            color = QColor(self.colors.get(entry['type'], '#000000'))
            bg_color = QColor(highlight_color) if highlight_color else QColor('#ffffff')
            
            items = [
                QTableWidgetItem(entry['timestamp']),
                QTableWidgetItem(entry['type']),
                QTableWidgetItem(parsed['key']),
                QTableWidgetItem(parsed['object']),
                QTableWidgetItem(parsed['location']),
                QTableWidgetItem(parsed['details'])
            ]
            
            for col, item in enumerate(items):
                if highlight_color:
                    item.setBackground(bg_color)
                    item.setForeground(QColor('#000000'))
                else:
                    item.setForeground(color)
                
                if col == 1:  # Колонка типа
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                
                # Применяем затемнение
                if float(opacity) < 1.0:
                    dimmed_color = QColor(color)
                    dimmed_color.setAlpha(int(255 * float(opacity)))
                    item.setForeground(dimmed_color)
                
                self.table_widget.setItem(row, col, item)
        
        self.table_widget.resizeColumnsToContents()
        
        # Синхронизируем вторую таблицу если она видна
        if hasattr(self, 'table_widget2') and self.table_widget2.isVisible():
            self.sync_tables()
    
    def setup_table_widget(self):
        # Создаем таблицу и заменяем текстовые поля
        self.table_widget = QTableWidget()
        self.table_widget.setFont(QFont("Consolas", 9))
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget.setSortingEnabled(True)
        
        # Настраиваем заголовки
        columns = ['Время', 'Тип', 'CKey', 'Объект', 'Локация', 'Детали']
        self.table_widget.setColumnCount(len(columns))
        self.table_widget.setHorizontalHeaderLabels(columns)
        
        # Контекстное меню для заголовков
        header = self.table_widget.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.show_table_column_menu)
        
        # Заменяем в сплиттере
        self.splitter.replaceWidget(0, self.table_widget)
        self.text_edit1.hide()
        
        # Применяем сохраненные настройки скрытых колонок
        self.apply_hidden_columns()
    
    def setup_second_table(self):
        self.table_widget2 = QTableWidget()
        self.table_widget2.setFont(QFont("Consolas", 9))
        self.table_widget2.setAlternatingRowColors(True)
        self.table_widget2.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget2.setSortingEnabled(True)
        
        # Настраиваем заголовки
        columns = ['Время', 'Тип', 'CKey', 'Объект', 'Локация', 'Детали']
        self.table_widget2.setColumnCount(len(columns))
        self.table_widget2.setHorizontalHeaderLabels(columns)
        
        # Контекстное меню для заголовков
        header2 = self.table_widget2.horizontalHeader()
        header2.setContextMenuPolicy(Qt.CustomContextMenu)
        header2.customContextMenuRequested.connect(lambda pos: self.show_table_column_menu(pos, table=2))
        
        # Не заменяем сразу, только при необходимости
        self.table_widget2.hide()
    
    def sync_tables(self):
        if not hasattr(self, 'table_widget2') or not hasattr(self, 'table_widget'):
            return
        
        # Копируем данные из первой таблицы во вторую
        self.table_widget2.setRowCount(self.table_widget.rowCount())
        
        for row in range(self.table_widget.rowCount()):
            for col in range(self.table_widget.columnCount()):
                item1 = self.table_widget.item(row, col)
                if item1:
                    item2 = QTableWidgetItem(item1.text())
                    item2.setForeground(item1.foreground())
                    item2.setBackground(item1.background())
                    item2.setFont(item1.font())
                    self.table_widget2.setItem(row, col, item2)
        
        self.table_widget2.resizeColumnsToContents()
    
    def show_table_column_menu(self, position, table=1):
        menu = QMenu(self)
        widget = self.table_widget if table == 1 else self.table_widget2
        
        for col in range(widget.columnCount()):
            header_text = widget.horizontalHeaderItem(col).text()
            action = QAction(header_text, self)
            action.setCheckable(True)
            action.setChecked(not widget.isColumnHidden(col))
            action.triggered.connect(lambda checked, c=col, t=table: self.toggle_table_column(c, checked, t))
            menu.addAction(action)
        
        menu.exec_(widget.horizontalHeader().mapToGlobal(position))
    
    def toggle_table_column(self, column, visible, table=1):
        widget = self.table_widget if table == 1 else self.table_widget2
        if visible:
            widget.showColumn(column)
        else:
            widget.hideColumn(column)
        
        # Сохраняем настройки при изменении
        if table == 1:
            self.save_settings()
    
    def parse_message(self, message, msg_type):
        result = {'key': '', 'object': '', 'location': '', 'details': message}
        
        # Парсинг для разных типов сообщений
        if msg_type == 'ACCESS':
            if 'Login:' in message:
                parts = message.split(' from ')
                if len(parts) >= 2:
                    result['key'] = parts[0].replace('Login: ', '')
                    result['location'] = parts[1].split(' ||')[0]
                    result['details'] = parts[1].split(' ||')[1] if '||' in parts[1] else ''
            elif 'Mob Login:' in message:
                result['key'] = message.split('/(')[0].replace('Mob Login: ', '')
                result['object'] = message.split('was assigned to a ')[1] if 'was assigned to a ' in message else ''
        
        elif msg_type == 'GAME':
            # Парсинг координат в скобках
            location_match = re.search(r'\(([^)]+)\)$', message)
            if location_match:
                result['location'] = location_match.group(1)
                result['details'] = message[:location_match.start()].strip()
            
            # Извлечение ключа/объекта
            if '/' in message:
                key_part = message.split('/')[0]
                if key_part.count('*') >= 2:
                    result['key'] = key_part.split('*')[1] if '*' in key_part else ''
                elif '(' in key_part:
                    result['object'] = key_part.split('(')[1].split(')')[0] if ')' in key_part else ''
        
        elif msg_type == 'EMOTE':
            # Парсинг эмоций
            if '/' in message:
                result['key'] = message.split('/')[0].replace('*no key*', '')
                result['object'] = message.split('(')[1].split(')')[0] if '(' in message and ')' in message else ''
                # Локация в конце
                location_match = re.search(r'\(([^)]+)\)$', message)
                if location_match:
                    result['location'] = location_match.group(1)
                    # Действие между объектом и локацией
                    action_part = message.split(') ')[1] if ') ' in message else ''
                    result['details'] = action_part.split(' (')[0] if ' (' in action_part else action_part
        
        elif msg_type == 'SAY':
            # Парсинг речи
            if '/' in message:
                result['key'] = message.split('/')[0].replace('*no key*', '')
                result['object'] = message.split('(')[1].split(')')[0] if '(' in message and ')' in message else ''
                # Текст в кавычках
                quote_match = re.search(r'"([^"]+)"', message)
                if quote_match:
                    result['details'] = quote_match.group(1)
                # Локация в конце
                location_match = re.search(r'\(([^)]+)\)$', message)
                if location_match:
                    result['location'] = location_match.group(1)
        
        elif msg_type == 'ADMIN':
            # Парсинг админских действий
            if 'created a' in message:
                result['key'] = message.split('/(')[0] if '/(' in message else ''
                result['object'] = message.split('created a ')[1] if 'created a ' in message else ''
                result['details'] = 'created'
        
        # Очистка пустых значений
        for key in result:
            if result[key]:
                result[key] = result[key].strip()
        
        return result
    
    def should_show_entry(self, entry):
        # Фильтр по типу
        type_visible = self.filter_checkboxes.get(entry['type'], QCheckBox()).isChecked()
        
        # Фильтр по дате
        date_ok = True
        if self.date_filter_enabled.isChecked() and entry['datetime'] and isinstance(entry['datetime'], datetime):
            date_from = self.date_from.dateTime().toPyDateTime()
            date_to = self.date_to.dateTime().toPyDateTime()
            date_ok = date_from <= entry['datetime'] <= date_to
        
        # Фильтр по ключу
        key_ok = True
        key_text = self.key_filter.text().strip()
        if key_text:
            key_ok = key_text.lower() in entry['message'].lower()
        
        if not (type_visible and date_ok and key_ok):
            if self.hide_radio.isChecked():
                return False
        
        return True
    
    def get_entry_opacity(self, entry):
        type_visible = self.filter_checkboxes.get(entry['type'], QCheckBox()).isChecked()
        
        date_ok = True
        if self.date_filter_enabled.isChecked() and entry['datetime'] and isinstance(entry['datetime'], datetime):
            date_from = self.date_from.dateTime().toPyDateTime()
            date_to = self.date_to.dateTime().toPyDateTime()
            date_ok = date_from <= entry['datetime'] <= date_to
        
        key_ok = True
        key_text = self.key_filter.text().strip()
        if key_text:
            key_ok = key_text.lower() in entry['message'].lower()
        
        return "0.3" if (not (type_visible and date_ok and key_ok) and self.dim_radio.isChecked()) else "1.0"
    
    def update_stats(self):
        if not self.log_data:
            return
            
        stats = {}
        for entry in self.log_data:
            stats[entry['type']] = stats.get(entry['type'], 0) + 1
        
        stats_text = f"Всего записей: {len(self.log_data)} | "
        stats_text += " | ".join([f"{k}: {v}" for k, v in stats.items()])
        self.stats_label.setText(stats_text)
    
    def apply_filters(self):
        if hasattr(self, 'log_data') and self.log_data:
            self.display_log()
    
    def on_search(self):
        self.apply_search_highlight()
    
    def apply_search_highlight(self):
        search_term = self.search_edit.text()
        
        if self.table_mode and hasattr(self, 'table_widget'):
            # Очищаем выделение
            self.table_widget.clearSelection()
            if hasattr(self, 'table_widget2') and self.table_widget2.isVisible():
                self.table_widget2.clearSelection()
            
            if search_term:
                # Поиск в таблице
                items = self.table_widget.findItems(search_term, Qt.MatchContains)
                for item in items:
                    item.setSelected(True)
                if hasattr(self, 'table_widget2') and self.table_widget2.isVisible():
                    items2 = self.table_widget2.findItems(search_term, Qt.MatchContains)
                    for item in items2:
                        item.setSelected(True)
        else:
            # Очищаем подсветку в тексте
            for text_edit in [self.text_edit1, self.text_edit2]:
                if not text_edit.isVisible():
                    continue
                # Перерисовываем без поиска
                if self.table_mode:
                    self.display_table_format()
                else:
                    self.display_text_format()
                
            if search_term:
                # Поиск в тексте
                for text_edit in [self.text_edit1, self.text_edit2]:
                    if not text_edit.isVisible():
                        continue
                        
                    cursor = text_edit.textCursor()
                    format_highlight = QTextCharFormat()
                    format_highlight.setBackground(QColor('#ffff00'))
                    
                    flags = QTextDocument.FindFlag(0)
                    if self.case_sensitive.isChecked():
                        flags |= QTextDocument.FindCaseSensitively
                    
                    cursor.movePosition(QTextCursor.Start)
                    while True:
                        try:
                            if self.regex_search.isChecked():
                                regex = QRegExp(search_term)
                                if not regex.isValid():
                                    break
                                cursor = text_edit.document().find(regex, cursor, flags)
                            else:
                                cursor = text_edit.document().find(search_term, cursor, flags)
                            if cursor.isNull():
                                break
                            cursor.mergeCharFormat(format_highlight)
                        except:
                            break
    
    def show_context_menu(self, position):
        sender = self.sender()
        menu = QMenu(self)
        
        copy_action = menu.addAction("📋 Копировать")
        copy_action.triggered.connect(sender.copy)
        
        select_all_action = menu.addAction("📄 Выделить все")
        select_all_action.triggered.connect(sender.selectAll)
        
        menu.addSeparator()
        
        save_action = menu.addAction("💾 Сохранить выделенное")
        save_action.triggered.connect(lambda: self.save_selection(sender))
        
        menu.exec_(sender.mapToGlobal(position))
    
    def save_selection(self, text_edit=None):
        if text_edit is None:
            text_edit = self.text_edit1
        selected_text = text_edit.textCursor().selectedText()
        if selected_text:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить выделенное", "", "Text files (*.txt);;All files (*.*)"
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(selected_text)
    
    def zoom_in(self):
        if self.table_mode and hasattr(self, 'table_widget'):
            font = self.table_widget.font()
            font.setPointSize(font.pointSize() + 1)
            self.table_widget.setFont(font)
            if hasattr(self, 'table_widget2'):
                self.table_widget2.setFont(font)
        else:
            if self.text_edit1.isVisible():
                self.text_edit1.zoomIn(2)
            if self.text_edit2.isVisible():
                self.text_edit2.zoomIn(2)
    
    def zoom_out(self):
        if self.table_mode and hasattr(self, 'table_widget'):
            font = self.table_widget.font()
            if font.pointSize() > 6:
                font.setPointSize(font.pointSize() - 1)
                self.table_widget.setFont(font)
                if hasattr(self, 'table_widget2'):
                    self.table_widget2.setFont(font)
        else:
            if self.text_edit1.isVisible():
                self.text_edit1.zoomOut(2)
            if self.text_edit2.isVisible():
                self.text_edit2.zoomOut(2)
    
    def clear_log(self):
        self.text_edit1.clear()
        self.text_edit2.clear()
        self.log_data = []
        self.stats_label.setText("Готов к загрузке логов")
        self.statusBar().showMessage("Очищено")
    
    def toggle_split(self):
        if self.table_mode:
            if not hasattr(self, 'table_widget2'):
                self.setup_second_table()
            
            if self.table_widget2.isVisible():
                self.table_widget2.hide()
            else:
                # Убеждаемся что вторая таблица в сплиттере
                if self.splitter.widget(1) != self.table_widget2:
                    self.splitter.replaceWidget(1, self.table_widget2)
                self.table_widget2.show()
                self.text_edit2.hide()
                # Копируем данные из первой таблицы
                self.sync_tables()
        else:
            if self.text_edit2.isVisible():
                self.text_edit2.hide()
            else:
                # Убеждаемся что text_edit2 в сплиттере
                if self.splitter.widget(1) != self.text_edit2:
                    self.splitter.replaceWidget(1, self.text_edit2)
                    if hasattr(self, 'table_widget2'):
                        self.table_widget2.hide()
                self.text_edit2.show()
    
    def toggle_table_mode(self):
        self.table_mode = not self.table_mode
        self.table_action.setText("📄 Текст" if self.table_mode else "📊 Таблица")
        
        if self.table_mode:
            # Переключаемся в табличный режим
            if not hasattr(self, 'table_widget'):
                self.setup_table_widget()
            else:
                # Возвращаем таблицу в сплиттер
                if self.splitter.widget(0) != self.table_widget:
                    self.splitter.replaceWidget(0, self.table_widget)
                self.table_widget.show()
                self.text_edit1.hide()
            
            # Проверяем вторую панель если разделение включено
            if self.text_edit2.isVisible():
                if not hasattr(self, 'table_widget2'):
                    self.setup_second_table()
                if self.splitter.widget(1) != self.table_widget2:
                    self.splitter.replaceWidget(1, self.table_widget2)
                self.table_widget2.show()
                self.text_edit2.hide()
                self.sync_tables()
            
            if hasattr(self, 'log_data') and self.log_data:
                self.display_log()
        else:
            # Переключаемся в текстовый режим
            if hasattr(self, 'table_widget') and self.splitter.widget(0) == self.table_widget:
                self.splitter.replaceWidget(0, self.text_edit1)
                self.table_widget.hide()
            
            # Проверяем вторую панель
            if hasattr(self, 'table_widget2') and self.splitter.widget(1) == self.table_widget2:
                self.splitter.replaceWidget(1, self.text_edit2)
                self.table_widget2.hide()
            
            self.text_edit1.show()
            if hasattr(self, 'log_data') and self.log_data:
                self.display_log()
    
    def configure_highlight_colors(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройка цветов подсветки")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        
        self.highlight_color_buttons = []
        
        for i in range(5):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"Текст {i+1}"))
            
            color_btn = QPushButton()
            color_btn.setStyleSheet(f"background-color: {self.highlight_colors[i]}")
            color_btn.clicked.connect(lambda checked, idx=i: self.change_highlight_color_in_dialog(idx))
            self.highlight_color_buttons.append(color_btn)
            row.addWidget(color_btn)
            
            layout.addLayout(row)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            self.apply_filters()
    
    def change_highlight_color(self, index):
        color = QColorDialog.getColor(QColor(self.highlight_colors[index]), self)
        if color.isValid():
            self.highlight_colors[index] = color.name()
            self.highlight_edits[index].setStyleSheet(f"background-color: {self.highlight_colors[index]}; color: #000;")
            self.save_settings()
    
    def change_highlight_color_in_dialog(self, index):
        color = QColorDialog.getColor(QColor(self.highlight_colors[index]), self)
        if color.isValid():
            self.highlight_colors[index] = color.name()
            self.highlight_edits[index].setStyleSheet(f"background-color: {self.highlight_colors[index]}; color: #000;")
            # Обновляем кнопку в диалоге
            self.highlight_color_buttons[index].setStyleSheet(f"background-color: {self.highlight_colors[index]}")
            self.save_settings()
    
    def configure_font(self):
        current_font = self.text_edit1.font()
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            self.text_edit1.setFont(font)
            self.text_edit2.setFont(font)
            if hasattr(self, 'table_widget'):
                self.table_widget.setFont(font)
            if hasattr(self, 'table_widget2'):
                self.table_widget2.setFont(font)
            self.save_settings()
    
    def configure_colors(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройка цветов")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        
        self.color_buttons = {}
        
        for event_type, color in self.colors.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(event_type))
            
            color_btn = QPushButton()
            color_btn.setStyleSheet(f"background-color: {color}")
            color_btn.clicked.connect(lambda checked, et=event_type: self.change_event_color_in_dialog(et))
            self.color_buttons[event_type] = color_btn
            row.addWidget(color_btn)
            
            layout.addLayout(row)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setStyleSheet(self.styleSheet())
        if dialog.exec_() == QDialog.Accepted:
            self.apply_filters()
    
    def change_event_color(self, event_type):
        color = QColorDialog.getColor(QColor(self.colors[event_type]), self)
        if color.isValid():
            self.colors[event_type] = color.name()
            # Обновляем цвет чекбокса
            self.filter_checkboxes[event_type].setStyleSheet(
                f"QCheckBox {{ color: {color.name()}; font-weight: bold; }}"
            )
            self.save_settings()
    
    def change_event_color_in_dialog(self, event_type):
        color = QColorDialog.getColor(QColor(self.colors[event_type]), self)
        if color.isValid():
            self.colors[event_type] = color.name()
            # Обновляем цвет чекбокса
            self.filter_checkboxes[event_type].setStyleSheet(
                f"QCheckBox {{ color: {color.name()}; font-weight: bold; }}"
            )
            # Обновляем кнопку в диалоге
            self.color_buttons[event_type].setStyleSheet(f"background-color: {color.name()}")
            self.save_settings()
    
    def show_regex_help(self):
        help_text = r"""Примеры регулярных выражений:

• .* - любые символы
• \d+ - одна или более цифр
• [Aa]dmin - Admin или admin
• ^ERROR - строки начинающиеся с ERROR
• CRASH$ - строки заканчивающиеся на CRASH
• (ERROR|FAIL) - ERROR или FAIL
• \w+ - одно или более слов"""
        
        QMessageBox.information(self, "Справка по регулярным выражениям", help_text)
    
    def open_investigation(self):
        if not self.log_data:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите лог-файл")
            return
        
        dialog = InvestigationDialog(self.log_data, self)
        # Применяем тему к диалогу
        dialog.setStyleSheet(self.styleSheet())
        dialog.exec_()
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                self.colors = settings.get('colors', {
                    'ACCESS': '#4CAF50', 'GAME': '#2196F3', 'EMOTE': '#FF9800',
                    'SAY': '#9C27B0', 'ADMIN': '#F44336', 'ERROR': '#FF0000'
                })
                
                self.highlight_colors = settings.get('highlight_colors', 
                    ['#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF'])
                
                font_settings = settings.get('font', {})
                if font_settings:
                    self.default_font = QFont(font_settings.get('family', 'Consolas'), 
                                            font_settings.get('size', 10))
                else:
                    self.default_font = QFont('Consolas', 10)
                
                self.current_theme = settings.get('theme', 'default')
                self.hidden_columns = settings.get('hidden_columns', [])
                self.workspace_color = settings.get('workspace_color', '#ffffff')
                    
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")
                self.set_default_settings()
        else:
            self.set_default_settings()
    
    def set_default_settings(self):
        self.colors = {
            'ACCESS': '#4CAF50', 'GAME': '#2196F3', 'EMOTE': '#FF9800',
            'SAY': '#9C27B0', 'ADMIN': '#F44336', 'ERROR': '#FF0000'
        }
        self.highlight_colors = ['#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF']
        self.default_font = QFont('Consolas', 10)
        self.current_theme = 'default'
        self.hidden_columns = []
        self.workspace_color = '#ffffff'
    

    
    def save_settings(self):
        settings = {
            'colors': self.colors,
            'highlight_colors': self.highlight_colors,
            'font': {
                'family': self.text_edit1.font().family(),
                'size': self.text_edit1.font().pointSize()
            },
            'theme': self.current_theme,
            'hidden_columns': self.get_hidden_columns(),
            'workspace_color': self.workspace_color
        }
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def get_hidden_columns(self):
        hidden_columns = []
        if hasattr(self, 'table_widget'):
            for col in range(self.table_widget.columnCount()):
                if self.table_widget.isColumnHidden(col):
                    hidden_columns.append(col)
        return hidden_columns
    
    def apply_hidden_columns(self):
        if hasattr(self, 'table_widget') and self.hidden_columns:
            for col in self.hidden_columns:
                if col < self.table_widget.columnCount():
                    self.table_widget.hideColumn(col)
                    if hasattr(self, 'table_widget2'):
                        self.table_widget2.hideColumn(col)
    
    def show_about(self):
        about_text = """
<h2>Shiptest Log Viewer Advanced</h2>
<p><b>Версия:</b> 1.0</p>
<p><b>Создатель:</b> MrCat15352</p>
<p>Все права принадлежат дискорд серверу<br>
<a href="https://discord.gg/celadon-1100198143456465067">Celadon</a></p>
<p><b>Нашли баг?</b><br>
Сообщите Head of Coding!</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("О программе")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.setStandardButtons(QMessageBox.Ok)
        # Исключение для диалога "О программе"
        msg.setStyleSheet("QMessageBox, QMessageBox QLabel, QMessageBox QPushButton { color: #000000; background-color: #ffffff; }")
        msg.exec_()
    
    def configure_theme(self):
        themes = {
            'default': 'Обычная',
            'pirate': 'Пиратская',
            'dark': 'Тёмная',
            'uplink': 'Uplink',
            'elysium': 'Элизиум',
            'light_grey': 'Светло-серая',
            'dark_grey': 'Тёмно-серая'
        }
        
        theme, ok = QInputDialog.getItem(self, 'Выбор темы', 'Тема:', 
                                        list(themes.values()), 
                                        list(themes.values()).index(themes[self.current_theme]), 
                                        False)
        if ok:
            for key, value in themes.items():
                if value == theme:
                    self.current_theme = key
                    break
            
            self.apply_theme()
            self.save_settings()
    
    def apply_theme(self):
        if self.current_theme == 'pirate':
            self.apply_pirate_theme()
        elif self.current_theme == 'dark':
            self.apply_dark_theme()
        elif self.current_theme == 'uplink':
            self.apply_uplink_theme()
        elif self.current_theme == 'elysium':
            self.apply_elysium_theme()
        elif self.current_theme == 'light_grey':
            self.apply_light_grey_theme()
        elif self.current_theme == 'dark_grey':
            self.apply_dark_grey_theme()
        else:
            self.apply_default_theme()
        
        # Применяем тему ко всему приложению
        QApplication.instance().setStyleSheet(self.styleSheet())
        # Применяем цвет рабочей области
        self.apply_workspace_color()
    
    def apply_pirate_theme(self):
        pirate_style = """
        * {
            color: #ffffff;
        }
        QMainWindow {
            background-color: #351c1c;
        }
        QToolBar {
            background-color: #743939;
            border: 1px solid #ce8787;
        }
        QToolBar QToolButton:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }
        QPushButton {
            background-color: #743939;
            border: 1px solid #ce8787;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #5e0000;
        }
        QPushButton:pressed {
            background-color: #910101;
        }
        QLineEdit {
            background-color: #351c1c;
            border: 1px solid #ce8787;
            padding: 3px;
        }
        QTextEdit {
            background-color: #351c1c;
            border: 1px solid #ce8787;
        }
        QTableWidget {
            background-color: #351c1c;
            alternate-background-color: #2a1515;
            gridline-color: #ce8787;
        }
        QHeaderView::section {
            background-color: #743939;
            border: 1px solid #ce8787;
        }
        QStatusBar {
            background-color: #743939;
        }
        QMenuBar {
            background-color: #743939;
        }
        QMenu {
            background-color: #351c1c;
            border: 1px solid #ce8787;
        }
        QMenu::item:selected {
            background-color: #743939;
        }
        QDialog {
            background-color: #351c1c;
        }
        QInputDialog {
            background-color: #351c1c;
        }
        QSpinBox {
            background-color: #351c1c;
            border: 1px solid #ce8787;
            padding: 3px;
        }
        QDateTimeEdit {
            background-color: #351c1c;
            border: 1px solid #ce8787;
            padding: 3px;
        }
        """
        self.setStyleSheet(pirate_style)
    
    def apply_dark_theme(self):
        dark_style = """
        * {
            color: #ffffff;
        }
        QMainWindow {
            background-color: #2b2b2b;
        }
        QToolBar {
            background-color: #3c3c3c;
            border: 1px solid #555555;
        }
        QToolBar QToolButton:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }
        QPushButton {
            background-color: #404040;
            border: 1px solid #555555;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
        QLineEdit {
            background-color: #404040;
            border: 1px solid #555555;
            padding: 3px;
        }
        QTextEdit {
            background-color: #2b2b2b;
            border: 1px solid #555555;
        }
        QTableWidget {
            background-color: #2b2b2b;
            alternate-background-color: #353535;
            gridline-color: #555555;
        }
        QHeaderView::section {
            background-color: #3c3c3c;
            border: 1px solid #555555;
        }
        QStatusBar {
            background-color: #3c3c3c;
        }
        QMenuBar {
            background-color: #3c3c3c;
        }
        QMenu {
            background-color: #2b2b2b;
            border: 1px solid #555555;
        }
        QMenu::item:selected {
            background-color: #404040;
        }
        QDialog {
            background-color: #2b2b2b;
        }
        QInputDialog {
            background-color: #2b2b2b;
        }
        QSpinBox {
            background-color: #404040;
            border: 1px solid #555555;
            padding: 3px;
        }
        QDateTimeEdit {
            background-color: #404040;
            border: 1px solid #555555;
            padding: 3px;
        }
        """
        self.setStyleSheet(dark_style)
    
    def apply_default_theme(self):
        self.setStyleSheet('')
    
    def apply_uplink_theme(self):
        uplink_style = """
        * {
            color: #ffffff;
        }
        QMainWindow {
            background-color: #1a1a1a;
        }
        QToolBar {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5d5041, stop:0.5 #40372d, stop:1 #5d5041);
            border: 2px solid #000000;
        }
        QToolBar QToolButton:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5d5041, stop:0.5 #40372d, stop:1 #5d5041);
            border: 2px solid #000000;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9c1e1e, stop:0.5 #6c2828, stop:1 #9c1e1e);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #515d6c, stop:0.5 #252a30, stop:1 #515d6c);
        }
        QLineEdit {
            background-color: rgba(0, 0, 0, 0.4);
            border: 2px solid #000000;
            padding: 3px;
        }
        QTextEdit {
            background-color: rgba(0, 0, 0, 0.4);
            border: 2px solid #000000;
        }
        QTableWidget {
            background-color: rgba(0, 0, 0, 0.4);
            alternate-background-color: rgba(0, 0, 0, 0.6);
            gridline-color: #000000;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5d5041, stop:0.5 #40372d, stop:1 #5d5041);
            border: 2px solid #000000;
        }
        QStatusBar {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5d5041, stop:0.5 #40372d, stop:1 #5d5041);
        }
        QMenuBar {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5d5041, stop:0.5 #40372d, stop:1 #5d5041);
        }
        QMenu {
            background-color: rgba(0, 0, 0, 0.4);
            border: 2px solid #000000;
        }
        QMenu::item:selected {
            background-color: #5d5041;
        }
        QDialog {
            background-color: #1a1a1a;
        }
        QInputDialog {
            background-color: #1a1a1a;
        }
        QSpinBox {
            background-color: rgba(0, 0, 0, 0.4);
            border: 2px solid #000000;
            padding: 3px;
        }
        QDateTimeEdit {
            background-color: rgba(0, 0, 0, 0.4);
            border: 2px solid #000000;
            padding: 3px;
        }
        """
        self.setStyleSheet(uplink_style)
    
    def apply_elysium_theme(self):
        elysium_style = """
        * {
            color: #00ff00;
        }
        QMainWindow {
            background-color: #0d3004;
        }
        QToolBar {
            background-color: #39743e;
            border: 1px solid #a1ce87;
        }
        QToolBar QToolButton:hover {
            background-color: rgba(0, 255, 0, 0.2);
        }
        QPushButton {
            background-color: #39743e;
            border: 1px solid #a1ce87;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #3c702f;
        }
        QPushButton:pressed {
            background-color: #4e9101;
        }
        QLineEdit {
            background-color: #0d3004;
            border: 1px solid #a1ce87;
            padding: 3px;
        }
        QTextEdit {
            background-color: #0d3004;
            border: 1px solid #a1ce87;
        }
        QTableWidget {
            background-color: #0d3004;
            alternate-background-color: #1a4008;
            gridline-color: #a1ce87;
        }
        QHeaderView::section {
            background-color: #39743e;
            border: 1px solid #a1ce87;
        }
        QStatusBar {
            background-color: #39743e;
        }
        QMenuBar {
            background-color: #39743e;
        }
        QMenu {
            background-color: #0d3004;
            border: 1px solid #a1ce87;
        }
        QMenu::item:selected {
            background-color: #39743e;
        }
        QDialog {
            background-color: #0d3004;
        }
        QInputDialog {
            background-color: #0d3004;
        }
        QSpinBox {
            background-color: #0d3004;
            border: 1px solid #a1ce87;
            padding: 3px;
        }
        QDateTimeEdit {
            background-color: #0d3004;
            border: 1px solid #a1ce87;
            padding: 3px;
        }
        """        
        self.setStyleSheet(elysium_style)
    
    def apply_light_grey_theme(self):
        light_grey_style = """
        * {
            color: #000000;
        }
        QMainWindow {
            background-color: #D0D0D0;
        }
        QToolBar {
            background-color: #C0C0C0;
            border: 1px solid #A0A0A0;
        }
        QToolBar QToolButton:hover {
            background-color: rgba(0, 0, 0, 0.1);
        }
        QPushButton {
            background-color: #E0E0E0;
            border: 1px solid #A0A0A0;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #F0F0F0;
        }
        QPushButton:pressed {
            background-color: #B0B0B0;
        }
        QLineEdit {
            background-color: #F0F0F0;
            border: 1px solid #A0A0A0;
            padding: 3px;
        }
        QTextEdit {
            background-color: #F0F0F0;
            border: 1px solid #A0A0A0;
        }
        QTableWidget {
            background-color: #F0F0F0;
            alternate-background-color: #E8E8E8;
            gridline-color: #A0A0A0;
        }
        QHeaderView::section {
            background-color: #C0C0C0;
            border: 1px solid #A0A0A0;
        }
        QStatusBar {
            background-color: #C0C0C0;
        }
        QMenuBar {
            background-color: #C0C0C0;
        }
        QMenu {
            background-color: #E0E0E0;
            border: 1px solid #A0A0A0;
        }
        QMenu::item:selected {
            background-color: #C0C0C0;
        }
        QDialog {
            background-color: #D0D0D0;
        }
        QInputDialog {
            background-color: #D0D0D0;
        }
        QSpinBox {
            background-color: #F0F0F0;
            border: 1px solid #A0A0A0;
            padding: 3px;
        }
        QDateTimeEdit {
            background-color: #F0F0F0;
            border: 1px solid #A0A0A0;
            padding: 3px;
        }
        """
        self.setStyleSheet(light_grey_style)
    
    def apply_dark_grey_theme(self):
        dark_grey_style = """
        * {
            color: #ffffff;
        }
        QMainWindow {
            background-color: #909090;
        }
        QToolBar {
            background-color: #808080;
            border: 1px solid #606060;
        }
        QToolBar QToolButton:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }
        QPushButton {
            background-color: #A0A0A0;
            border: 1px solid #606060;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #B0B0B0;
        }
        QPushButton:pressed {
            background-color: #707070;
        }
        QLineEdit {
            background-color: #A0A0A0;
            border: 1px solid #606060;
            padding: 3px;
        }
        QTextEdit {
            background-color: #A0A0A0;
            border: 1px solid #606060;
        }
        QTableWidget {
            background-color: #A0A0A0;
            alternate-background-color: #959595;
            gridline-color: #606060;
        }
        QHeaderView::section {
            background-color: #808080;
            border: 1px solid #606060;
        }
        QStatusBar {
            background-color: #808080;
        }
        QMenuBar {
            background-color: #808080;
        }
        QMenu {
            background-color: #A0A0A0;
            border: 1px solid #606060;
        }
        QMenu::item:selected {
            background-color: #808080;
        }
        QDialog {
            background-color: #909090;
        }
        QInputDialog {
            background-color: #909090;
        }
        QSpinBox {
            background-color: #A0A0A0;
            border: 1px solid #606060;
            padding: 3px;
        }
        QDateTimeEdit {
            background-color: #A0A0A0;
            border: 1px solid #606060;
            padding: 3px;
        }
        """
        self.setStyleSheet(dark_grey_style)
    
    def configure_workspace_color(self):
        color = QColorDialog.getColor(QColor(self.workspace_color), self)
        if color.isValid():
            self.workspace_color = color.name()
            self.apply_workspace_color()
            self.save_settings()
    
    def apply_workspace_color(self):
        workspace_style = f"""
        QTextEdit {{
            background-color: {self.workspace_color} !important;
        }}
        QTableWidget {{
            background-color: {self.workspace_color} !important;
        }}
        """
        # Применяем дополнительные стили поверх темы
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + workspace_style)
        QApplication.instance().setStyleSheet(self.styleSheet())

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Современный стиль
    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()