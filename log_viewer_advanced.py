import sys
import re
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from investigation_dialog import InvestigationDialog
from settings_dialog import SettingsDialog
from concurrent.futures import ThreadPoolExecutor
import threading

class LogViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shiptest Log Viewer Advanced")

        self.colors = {
            'ACCESS': '#4CAF50', 'GAME': '#2196F3', 'EMOTE': '#FF9800',
            'SAY': '#9C27B0', 'ADMIN': '#F44336', 'ERROR': '#FF0000'
        }

        self.table_mode = False
        self.log_data = []
        self.current_page = 0
        self.page_size = 1000
        self.settings_file = 'log_viewer_settings.json'
        self.load_settings()

        # Устанавливаем позицию и размер окна
        if 'main' in self.window_positions:
            pos = self.window_positions['main']
            self.setGeometry(pos['x'], pos['y'], pos.get('width', 1400), pos.get('height', 900))
        else:
            self.setGeometry(100, 100, 1400, 900)

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

        settings_action = QAction("⚙️ Настройки", self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)

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
        self.search_edit.returnPressed.connect(self.on_search)
        search_layout.addWidget(self.search_edit)

        search_btn = QPushButton("Поиск")
        search_btn.clicked.connect(self.on_search)
        search_layout.addWidget(search_btn)

        clear_search_btn = QPushButton("✕")
        clear_search_btn.setMaximumWidth(25)
        clear_search_btn.clicked.connect(lambda: self.search_edit.clear())
        search_layout.addWidget(clear_search_btn)

        self.case_sensitive = QCheckBox("Учитывать регистр")
        search_layout.addWidget(self.case_sensitive)

        self.regex_search = QCheckBox("Regex")
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
        self.filter_layout = filter_layout  # Сохраняем ссылку для динамического обновления

        # Создаем фильтры для базовых типов
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
        self.key_filter.returnPressed.connect(self.apply_filters)
        date_filter_layout.addWidget(self.key_filter)

        key_search_btn = QPushButton("Поиск")
        key_search_btn.clicked.connect(self.apply_filters)
        date_filter_layout.addWidget(key_search_btn)

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
        highlight_layout.setSpacing(3)
        highlight_layout.addWidget(QLabel("Подсветка строк:"))

        self.highlight_edits = []

        for i in range(5):
            edit = QLineEdit()
            edit.setPlaceholderText(f"Текст {i+1}")
            edit.setStyleSheet(f"background-color: {self.highlight_colors[i]}; color: #000;")
            edit.returnPressed.connect(self.apply_filters)
            self.highlight_edits.append(edit)
            highlight_layout.addWidget(edit)

            clear_btn = QPushButton("✕")
            clear_btn.setMaximumWidth(20)
            clear_btn.clicked.connect(lambda checked, idx=i: self.highlight_edits[idx].clear())
            highlight_layout.addWidget(clear_btn)

        highlight_search_btn = QPushButton("Поиск")
        highlight_search_btn.clicked.connect(self.apply_filters)
        highlight_layout.addWidget(highlight_search_btn)



        layout.addLayout(highlight_layout)

        # Пагинация
        pagination_layout = QHBoxLayout()
        pagination_layout.addWidget(QLabel("Страница:"))

        self.prev_btn = QPushButton("◀ Назад")
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setEnabled(False)
        pagination_layout.addWidget(self.prev_btn)

        self.page_label = QLabel("1 / 1")
        pagination_layout.addWidget(self.page_label)

        self.next_btn = QPushButton("Вперед ▶")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        pagination_layout.addWidget(self.next_btn)

        pagination_layout.addWidget(QLabel("Размер страницы:"))
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["1000", "2500", "5000", "10000", "20000", "30000", "40000", "50000"])
        self.page_size_combo.setCurrentText("1000")
        self.page_size_combo.currentTextChanged.connect(self.change_page_size)
        pagination_layout.addWidget(self.page_size_combo)

        pagination_layout.addStretch()
        layout.addLayout(pagination_layout)

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

                # Проверяем размер файла - увеличенные лимиты
                file_size = os.path.getsize(file_path)
                if file_size > 200 * 1024 * 1024:  # 200MB
                    reply = QMessageBox.question(self, "Большой файл",
                        f"Файл большой ({file_size // (1024*1024)} MB). Загрузить только последние 10,000 строк?",
                        QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        self.load_log_tail(file_path, 100000)
                    elif reply == QMessageBox.No:
                        return
                else:
                    # Читаем весь файл
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.parse_log(content)

                self.update_filter_checkboxes()
                self.display_log()
                self.update_stats()
                self.statusBar().showMessage(f"Загружено: {file_path}")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {e}")
                self.statusBar().showMessage("Ошибка загрузки")

    def load_log_tail(self, file_path, max_lines):
        """Загружает только последние N строк файла"""
        lines = []
        with open(file_path, 'r', encoding='utf-8') as f:
            # Читаем файл с конца
            f.seek(0, 2)  # Переходим в конец
            file_size = f.tell()

            # Читаем блоками с конца
            block_size = 8192
            blocks = []

            for i in range(0, file_size, block_size):
                f.seek(max(0, file_size - i - block_size))
                block = f.read(min(block_size, file_size - max(0, file_size - i - block_size)))
                blocks.append(block)

                # Подсчитываем строки
                total_lines = sum(block.count('\n') for block in blocks)
                if total_lines >= max_lines:
                    break

            # Объединяем блоки и берем последние строки
            content = ''.join(reversed(blocks))
            all_lines = content.split('\n')
            lines = all_lines[-max_lines:] if len(all_lines) > max_lines else all_lines

        content = '\n'.join(lines)
        self.parse_log(content)

    def load_log_chunked(self, file_path, max_records=500000):
        """Загружает файл по частям с агрессивными лимитами"""
        progress = QProgressDialog("Загрузка файла...", "Отмена", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()

        self.log_data = []
        chunk_size = 64 * 1024  # Меньшие чанки - 64KB

        with open(file_path, 'r', encoding='utf-8') as f:
            f.seek(0, 2)
            file_size = f.tell()
            f.seek(0)

            buffer = ""
            bytes_read = 0

            while True:
                if progress.wasCanceled():
                    break

                chunk = f.read(chunk_size)
                if not chunk:
                    break

                bytes_read += len(chunk)
                progress.setValue(int(bytes_read * 100 / file_size))
                QApplication.processEvents()

                buffer += chunk

                # Обрабатываем полные строки
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.parse_single_line(line, len(self.log_data) + 1)

                    # Жесткий лимит записей
                    if len(self.log_data) >= max_records:
                        QMessageBox.warning(self, "Лимит памяти",
                            f"Достигнут лимит в {max_records} записей. Загрузка остановлена.")
                        progress.close()
                        return

            # Обрабатываем последнюю строку
            if buffer.strip():
                self.parse_single_line(buffer, len(self.log_data) + 1)

        progress.close()

    def parse_single_line(self, line, line_num):
        """Парсит одну строку лога"""
        if line.strip():
            pattern = r'\[([^\]]+)\] (\w+(?:\s*\([^)]+\))?): (.+)'
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
            else:
                # Обрабатываем строки без типа (например системные сообщения)
                timestamp_pattern = r'\[([^\]]+)\] (.+)'
                timestamp_match = re.match(timestamp_pattern, line)
                if timestamp_match:
                    timestamp, message = timestamp_match.groups()
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
                        'type': 'SYSTEM',
                        'message': message,
                        'full_line': line
                    })
                else:
                    # Строки без временной метки (например разделители)
                    self.log_data.append({
                        'line_num': line_num,
                        'timestamp': '',
                        'datetime': None,
                        'type': 'OTHER',
                        'message': line,
                        'full_line': line
                    })

    def parse_log(self, content):
        self.log_data = []
        lines = content.split('\n')

        if len(lines) > 5000:
            self.parse_log_with_progress(lines)
        else:
            self.parse_log_fast(lines)

    def parse_log_fast(self, lines):
        # Максимально быстрый парсинг без лишних проверок
        pattern = re.compile(r'\[([^\]]+)\] (\w+(?:\s*\([^)]+\))?): (.+)')
        timestamp_pattern = re.compile(r'\[([^\]]+)\] (.+)')

        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue
            match = pattern.match(line)
            if match:
                timestamp, event_type, message = match.groups()
                self.log_data.append({
                    'line_num': line_num,
                    'timestamp': timestamp,
                    'datetime': None,  # Парсим дату только при необходимости
                    'type': event_type,
                    'message': message,
                    'full_line': line
                })
            else:
                # Обрабатываем строки без типа
                timestamp_match = timestamp_pattern.match(line)
                if timestamp_match:
                    timestamp, message = timestamp_match.groups()
                    self.log_data.append({
                        'line_num': line_num,
                        'timestamp': timestamp,
                        'datetime': None,
                        'type': 'SYSTEM',
                        'message': message,
                        'full_line': line
                    })
                else:
                    # Строки без временной метки
                    self.log_data.append({
                        'line_num': line_num,
                        'timestamp': '',
                        'datetime': None,
                        'type': 'OTHER',
                        'message': line,
                        'full_line': line
                    })

    def parse_log_with_progress(self, lines):
        progress = QProgressDialog("Парсинг лог-файла...", "Отмена", 0, len(lines), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()

        pattern = re.compile(r'\[([^\]]+)\] (\w+(?:\s*\([^)]+\))?): (.+)')
        timestamp_pattern = re.compile(r'\[([^\]]+)\] (.+)')
        batch_size = 1000  # Обрабатываем батчами

        for i in range(0, len(lines), batch_size):
            if progress.wasCanceled():
                break

            batch = lines[i:i + batch_size]
            for line_num, line in enumerate(batch, i + 1):
                if not line.strip():
                    continue
                match = pattern.match(line)
                if match:
                    timestamp, event_type, message = match.groups()
                    self.log_data.append({
                        'line_num': line_num,
                        'timestamp': timestamp,
                        'datetime': None,  # Ленивый парсинг дат
                        'type': event_type,
                        'message': message,
                        'full_line': line
                    })
                else:
                    # Обрабатываем строки без типа
                    timestamp_match = timestamp_pattern.match(line)
                    if timestamp_match:
                        timestamp, message = timestamp_match.groups()
                        self.log_data.append({
                            'line_num': line_num,
                            'timestamp': timestamp,
                            'datetime': None,
                            'type': 'SYSTEM',
                            'message': message,
                            'full_line': line
                        })
                    else:
                        # Строки без временной метки
                        self.log_data.append({
                            'line_num': line_num,
                            'timestamp': '',
                            'datetime': None,
                            'type': 'OTHER',
                            'message': line,
                            'full_line': line
                        })

            progress.setValue(i + batch_size)
            QApplication.processEvents()  # Обновляем UI

        progress.close()

    def parse_datetime_lazy(self, entry):
        # Парсим дату только когда нужно
        if entry['datetime'] is None:
            timestamp = entry['timestamp']
            try:
                entry['datetime'] = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    entry['datetime'] = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    entry['datetime'] = False  # Помечаем как неудачный парсинг
        return entry['datetime']

    def display_log(self):
        self.text_edit1.clear()
        self.text_edit2.clear()

        if self.table_mode:
            self.display_table_format()
        else:
            self.display_text_format()

        self.apply_search_highlight()

    def display_text_format(self):
        # Фильтруем записи с прогресс баром для больших объемов
        visible_entries = []

        if len(self.log_data) > 10000:
            progress = QProgressDialog("Обработка записей...", "Отмена", 0, len(self.log_data), self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            for i, entry in enumerate(self.log_data):
                if progress.wasCanceled():
                    break
                if i % 1000 == 0:
                    progress.setValue(i)
                    QApplication.processEvents()
                if self.should_show_entry(entry):
                    visible_entries.append(entry)

            progress.close()
        else:
            for entry in self.log_data:
                if self.should_show_entry(entry):
                    visible_entries.append(entry)

        # Пагинация
        total_pages = max(1, (len(visible_entries) + self.page_size - 1) // self.page_size)
        self.current_page = min(self.current_page, total_pages - 1)

        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(visible_entries))
        page_entries = visible_entries[start_idx:end_idx]

        # Обновляем элементы пагинации
        self.page_label.setText(f"{self.current_page + 1} / {total_pages}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)

        if len(visible_entries) > self.page_size:
            self.statusBar().showMessage(f"Показано {len(page_entries)} из {len(visible_entries)} строк (страница {self.current_page + 1}/{total_pages})")

        visible_entries = page_entries

        html_content = "<pre style='font-family: Consolas, monospace; font-size: 10pt;'>"

        search_term = self.search_edit.text().strip()

        for entry in visible_entries:
            line = entry['full_line']
            color = self.colors.get(entry['type'], '#000000')

            # Проверяем подсветку строк
            highlight_color = None
            for i, edit in enumerate(self.highlight_edits):
                text = edit.text().strip()
                if text and text.upper() in entry['full_line'].upper():
                    highlight_color = self.highlight_colors[i]
                    break

            # Подсвечиваем найденный текст
            display_line = line
            if search_term:
                if self.case_sensitive.isChecked():
                    if search_term in entry['full_line']:
                        display_line = line.replace(search_term, f"<span style='background-color: #ffff00; color: #000;'>{search_term}</span>")
                else:
                    if search_term.upper() in entry['full_line'].upper():
                        import re
                        pattern = re.compile(re.escape(search_term), re.IGNORECASE)
                        display_line = pattern.sub(lambda m: f"<span style='background-color: #ffff00; color: #000;'>{m.group()}</span>", line)

            if highlight_color:
                html_content += f"<div style='background-color: {highlight_color}; color: #000; font-weight: bold;'>{display_line}</div>"
            else:
                html_content += f"<div style='color: {color}; font-weight: bold;'>{display_line}</div>"

        html_content += "</pre>"
        self.text_edit1.setHtml(html_content)
        self.text_edit2.setHtml(html_content)

    def display_table_format(self):
        if not hasattr(self, 'table_widget'):
            self.setup_table_widget()

        # Фильтруем записи для таблицы
        filtered_entries = []
        for entry in self.log_data:
            if self.should_show_entry(entry):
                filtered_entries.append(entry)

        # Пагинация для таблицы
        total_pages = max(1, (len(filtered_entries) + self.page_size - 1) // self.page_size)
        self.current_page = min(self.current_page, total_pages - 1)

        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(filtered_entries))
        page_entries = filtered_entries[start_idx:end_idx]

        # Обновляем элементы пагинации
        self.page_label.setText(f"{self.current_page + 1} / {total_pages}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)

        if len(filtered_entries) > self.page_size:
            self.statusBar().showMessage(f"Показано {len(page_entries)} из {len(filtered_entries)} строк (страница {self.current_page + 1}/{total_pages})")

        # Собираем данные для таблицы
        table_data = []
        for entry in page_entries:

            parsed = self.parse_message(entry['message'], entry['type'])

            # Проверяем подсветку строк
            highlight_color = None
            search_term = self.search_edit.text().strip()

            for i, edit in enumerate(self.highlight_edits):
                text = edit.text().strip()
                if text and text.upper() in entry['full_line'].upper():
                    highlight_color = self.highlight_colors[i]
                    break

            # Проверяем поиск для таблицы
            is_search_match = False
            if search_term:
                if self.case_sensitive.isChecked():
                    is_search_match = search_term in entry['full_line']
                else:
                    is_search_match = search_term.upper() in entry['full_line'].upper()

            opacity = float(self.get_entry_opacity(entry))

            table_data.append({
                'entry': entry,
                'parsed': parsed,
                'highlight_color': highlight_color,
                'opacity': opacity
            })

        # Показываем прогресс для больших таблиц
        if len(table_data) > 1000:  # Уменьшен порог
            progress = QProgressDialog("Заполнение таблицы...", "Отмена", 0, len(table_data), self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

        # Заполняем таблицу
        self.table_widget.setRowCount(len(table_data))

        for row, data in enumerate(table_data):
            if len(table_data) > 1000 and row % 100 == 0:  # Чаще обновляем прогресс
                if 'progress' in locals() and progress.wasCanceled():
                    break
                if 'progress' in locals():
                    progress.setValue(row)
                QApplication.processEvents()

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
                # Применяем стиль в зависимости от настроек
                if highlight_color:
                    item.setBackground(bg_color)
                    item.setForeground(QColor('#000000'))
                elif is_search_match:
                    item.setBackground(QColor('#ffff00'))
                    item.setForeground(QColor('#000000'))
                else:
                    # Цвет только для колонки типа
                    if col == 1:
                        item.setForeground(color)

                if col == 1:  # Колонка типа
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

                # Применяем затемнение
                if float(opacity) < 1.0 and not (highlight_color or is_search_match):
                    current_color = item.foreground().color()
                    dimmed_color = QColor(current_color)
                    dimmed_color.setAlpha(int(255 * float(opacity)))
                    item.setForeground(dimmed_color)

                self.table_widget.setItem(row, col, item)

        if 'progress' in locals():
            progress.close()

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

        # Фильтр по дате с ленивым парсингом
        date_ok = True
        if self.date_filter_enabled.isChecked():
            dt = self.parse_datetime_lazy(entry)
            if dt and isinstance(dt, datetime):
                date_from = self.date_from.dateTime().toPyDateTime()
                date_to = self.date_to.dateTime().toPyDateTime()
                date_ok = date_from <= dt <= date_to

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
        if self.date_filter_enabled.isChecked():
            dt = self.parse_datetime_lazy(entry)
            if dt and isinstance(dt, datetime):
                date_from = self.date_from.dateTime().toPyDateTime()
                date_to = self.date_to.dateTime().toPyDateTime()
                date_ok = date_from <= dt <= date_to

        key_ok = True
        key_text = self.key_filter.text().strip()
        if key_text:
            key_ok = key_text.lower() in entry['message'].lower()

        return "0.3" if (not (type_visible and date_ok and key_ok) and self.dim_radio.isChecked()) else "1.0"

    def update_filter_checkboxes(self):
        # Находим все уникальные типы в данных
        found_types = set(entry['type'] for entry in self.log_data)

        # Добавляем новые типы
        for event_type in found_types:
            if event_type not in self.filter_checkboxes:
                # Используем цвет из настроек или цвет по умолчанию
                color = self.colors.get(event_type, '#888888')

                cb = QCheckBox(event_type)
                cb.setChecked(True)
                cb.setStyleSheet(f"QCheckBox {{ color: {color}; font-weight: bold; }}")
                cb.stateChanged.connect(self.apply_filters)
                self.filter_checkboxes[event_type] = cb

                # Вставляем перед stretch
                self.filter_layout.insertWidget(self.filter_layout.count() - 1, cb)

    def update_stats(self):
        if not self.log_data:
            return

        stats = {}
        visible_count = 0
        for entry in self.log_data:
            stats[entry['type']] = stats.get(entry['type'], 0) + 1
            if self.should_show_entry(entry):
                visible_count += 1

        stats_text = f"Всего записей: {len(self.log_data)} | Видимых: {visible_count} | "
        stats_text += " | ".join([f"{k}: {v}" for k, v in stats.items()])
        self.stats_label.setText(stats_text)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_log()

    def next_page(self):
        self.current_page += 1
        self.display_log()

    def change_page_size(self, size_text):
        self.page_size = int(size_text)
        self.current_page = 0
        self.display_log()

    def apply_filters(self):
        self.current_page = 0  # Сбрасываем на первую страницу
        if hasattr(self, 'log_data') and self.log_data:
            self.display_log()

    def on_search(self):
        self.apply_search_highlight()

    def apply_search_highlight(self):
        # Поиск работает только в пределах текущей страницы
        if hasattr(self, 'log_data') and self.log_data:
            if self.table_mode:
                self.display_table_format()
            else:
                self.display_text_format()

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

        # Получаем все типы из фильтров (включая динамически добавленные)
        all_types = {}
        for event_type in self.filter_checkboxes.keys():
            all_types[event_type] = self.colors.get(event_type, '#888888')

        for event_type, color in all_types.items():
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
        current_color = self.colors.get(event_type, '#888888')
        color = QColorDialog.getColor(QColor(current_color), self)
        if color.isValid():
            self.colors[event_type] = color.name()
            # Обновляем цвет чекбокса
            if event_type in self.filter_checkboxes:
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

        # Восстанавливаем позицию
        if 'investigation' in self.window_positions:
            pos = self.window_positions['investigation']
            dialog.move(pos['x'], pos['y'])

        dialog.show()

        # Сохраняем позицию при закрытии
        def save_position():
            self.window_positions['investigation'] = {'x': dialog.x(), 'y': dialog.y()}
            self.save_settings()
        dialog.finished.connect(save_position)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                self.colors = settings.get('colors', {
                    'ACCESS': '#4CAF50', 'GAME': '#2196F3', 'EMOTE': '#FF9800',
                    'SAY': '#9C27B0', 'ADMIN': '#F44336', 'ERROR': '#FF0000',
                    'SYSTEM': '#808080', 'OTHER': '#606060', 'SUBTLER': '#E91E63'
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
                self.table_style = settings.get('table_style', 'alternating')
                # Проверяем что стиль существует
                if self.table_style not in ['alternating', 'solid']:
                    self.table_style = 'alternating'

                self.window_positions = settings.get('window_positions', {})

            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")
                self.set_default_settings()
        else:
            self.set_default_settings()

    def set_default_settings(self):
        self.colors = {
            'ACCESS': '#4CAF50', 'GAME': '#2196F3', 'EMOTE': '#FF9800',
            'SAY': '#9C27B0', 'ADMIN': '#F44336', 'ERROR': '#FF0000',
            'SYSTEM': '#808080', 'OTHER': '#606060', 'SUBTLER': '#E91E63'
        }
        self.highlight_colors = ['#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF']
        self.default_font = QFont('Consolas', 10)
        self.current_theme = 'default'
        self.hidden_columns = []
        self.workspace_color = '#ffffff'
        self.table_style = 'alternating'  # alternating, solid
        self.window_positions = {}



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
            'workspace_color': self.workspace_color,
            'table_style': self.table_style,
            'window_positions': self.window_positions
        }

        # Сохраняем позицию главного окна
        self.window_positions['main'] = {
            'x': self.x(), 'y': self.y(),
            'width': self.width(), 'height': self.height()
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
<p><b>Версия:</b> 1.2</p>
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

        dialog = QInputDialog(self)
        dialog.setStyleSheet("QInputDialog, QInputDialog QLabel, QInputDialog QPushButton, QInputDialog QComboBox { color: #000000; background-color: #ffffff; }")
        dialog.setWindowTitle('Выбор темы')
        dialog.setLabelText('Тема:')
        dialog.setComboBoxItems(list(themes.values()))
        dialog.setTextValue(themes[self.current_theme])

        if dialog.exec_() == QDialog.Accepted:
            theme = dialog.textValue()
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
        # Применяем стиль таблиц
        self.apply_table_style()

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

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.setStyleSheet("QDialog, QDialog QLabel, QDialog QPushButton, QDialog QComboBox, QDialog QGroupBox, QDialog QTabWidget, QDialog QTabBar { color: #000000; background-color: #ffffff; }")

        # Восстанавливаем позицию
        if 'settings' in self.window_positions:
            pos = self.window_positions['settings']
            dialog.move(pos['x'], pos['y'])

        dialog.exec_()

        # Сохраняем позицию
        self.window_positions['settings'] = {'x': dialog.x(), 'y': dialog.y()}
        self.save_settings()

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

    def configure_table_style(self):
        styles = {
            'alternating': 'Чередующиеся строки',
            'solid': 'Однотонный фон'
        }

        dialog = QInputDialog(self)
        dialog.setStyleSheet("QInputDialog, QInputDialog QLabel, QInputDialog QPushButton, QInputDialog QComboBox { color: #000000; background-color: #ffffff; }")
        dialog.setWindowTitle('Выбор стиля таблиц')
        dialog.setLabelText('Стиль:')
        dialog.setComboBoxItems(list(styles.values()))
        dialog.setTextValue(styles.get(self.table_style, styles['alternating']))

        if dialog.exec_() == QDialog.Accepted:
            style = dialog.textValue()
            for key, value in styles.items():
                if value == style:
                    self.table_style = key
                    break

            self.apply_table_style()
            self.save_settings()

    def apply_table_style(self):
        if not hasattr(self, 'table_widget'):
            return

        if self.table_style == 'alternating':
            self.table_widget.setAlternatingRowColors(True)
            if hasattr(self, 'table_widget2'):
                self.table_widget2.setAlternatingRowColors(True)
        else:  # solid
            self.table_widget.setAlternatingRowColors(False)
            if hasattr(self, 'table_widget2'):
                self.table_widget2.setAlternatingRowColors(False)

        # Перерисовываем таблицу
        if hasattr(self, 'log_data') and self.log_data and self.table_mode:
            self.display_log()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Современный стиль
    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
