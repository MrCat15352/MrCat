import sys
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLineEdit, QLabel, QCheckBox, 
                             QTextEdit, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCharFormat, QColor, QFont

class LogViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SS13 Log Viewer (PyQt)")
        self.setGeometry(100, 100, 1200, 800)
        
        self.colors = {
            'ACCESS': QColor('#4CAF50'),
            'GAME': QColor('#2196F3'),
            'EMOTE': QColor('#FF9800'),
            'SAY': QColor('#9C27B0'),
            'ADMIN': QColor('#F44336'),
            'ERROR': QColor('#FF0000'),
            'CRITICAL': QColor('#8B0000')
        }
        
        self.log_data = []
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Панель управления
        control_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Открыть лог")
        self.load_btn.clicked.connect(self.load_log)
        control_layout.addWidget(self.load_btn)
        
        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.clicked.connect(self.clear_log)
        control_layout.addWidget(self.clear_btn)
        
        control_layout.addWidget(QLabel("Поиск:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.on_search)
        control_layout.addWidget(self.search_edit)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Фильтры
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтры:"))
        
        self.filter_checkboxes = {}
        for event_type in self.colors.keys():
            cb = QCheckBox(event_type)
            cb.setChecked(True)
            cb.stateChanged.connect(self.apply_filters)
            self.filter_checkboxes[event_type] = cb
            filter_layout.addWidget(cb)
        
        filter_layout.addWidget(QLabel("Критичные:"))
        self.critical_edit = QLineEdit("ERROR,CRASH,FAIL,EXCEPTION")
        self.critical_edit.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.critical_edit)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Текстовое поле
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Consolas", 10))
        layout.addWidget(self.text_edit)
        
    def load_log(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите лог файл", "", "Log files (*.log);;All files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.parse_log(content)
                self.display_log()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {e}")
    
    def parse_log(self, content):
        self.log_data = []
        pattern = r'\[([^\]]+)\] (\w+): (.+)'
        
        for line in content.split('\n'):
            if line.strip():
                match = re.match(pattern, line)
                if match:
                    timestamp, event_type, message = match.groups()
                    self.log_data.append({
                        'timestamp': timestamp,
                        'type': event_type,
                        'message': message,
                        'full_line': line
                    })
                else:
                    self.log_data.append({
                        'timestamp': '',
                        'type': 'OTHER',
                        'message': line,
                        'full_line': line
                    })
    
    def display_log(self):
        self.text_edit.clear()
        
        critical_words = [w.strip().upper() for w in self.critical_edit.text().split(',') if w.strip()]
        
        for entry in self.log_data:
            if not self.filter_checkboxes.get(entry['type'], QCheckBox()).isChecked():
                continue
            
            cursor = self.text_edit.textCursor()
            cursor.movePosition(cursor.End)
            
            # Формат для обычного текста
            format_normal = QTextCharFormat()
            
            # Формат для типа события
            format_event = QTextCharFormat()
            if entry['type'] in self.colors:
                format_event.setForeground(self.colors[entry['type']])
                format_event.setFontWeight(QFont.Bold)
            
            # Формат для критичных слов
            format_critical = QTextCharFormat()
            format_critical.setBackground(QColor('#FFEB3B'))
            format_critical.setForeground(QColor('#D32F2F'))
            
            # Проверка на критичные слова
            is_critical = any(word in entry['message'].upper() for word in critical_words)
            
            if is_critical:
                cursor.insertText(entry['full_line'] + '\n', format_critical)
            elif entry['type'] in self.colors:
                cursor.insertText(entry['full_line'] + '\n', format_event)
            else:
                cursor.insertText(entry['full_line'] + '\n', format_normal)
        
        self.apply_search_highlight()
    
    def apply_filters(self):
        if hasattr(self, 'log_data') and self.log_data:
            self.display_log()
    
    def on_search(self):
        self.apply_search_highlight()
    
    def apply_search_highlight(self):
        search_term = self.search_edit.text()
        if not search_term:
            return
        
        cursor = self.text_edit.textCursor()
        format_highlight = QTextCharFormat()
        format_highlight.setBackground(QColor('#FFFF00'))
        
        # Поиск и подсветка
        cursor.movePosition(cursor.Start)
        while not cursor.isNull() and not cursor.atEnd():
            cursor = self.text_edit.document().find(search_term, cursor)
            if not cursor.isNull():
                cursor.mergeCharFormat(format_highlight)
    
    def clear_log(self):
        self.text_edit.clear()
        self.log_data = []

def main():
    app = QApplication(sys.argv)
    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()