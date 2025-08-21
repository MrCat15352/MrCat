from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("⚙️ Настройки")
        self.setGeometry(300, 300, 600, 500)
        self.setModal(True)
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Создаем вкладки
        tabs = QTabWidget()
        
        # Вкладка "Цвета"
        colors_tab = QWidget()
        colors_layout = QVBoxLayout(colors_tab)
        colors_layout.setSpacing(5)
        
        # Цвета типов
        colors_group = QGroupBox("Цвета типов событий")
        colors_group_layout = QGridLayout(colors_group)
        colors_group_layout.setSpacing(2)
        colors_group_layout.setContentsMargins(5, 5, 5, 5)
        colors_group_layout.setVerticalSpacing(2)
        
        self.color_buttons = {}
        row = 0
        for event_type in ['ACCESS', 'GAME', 'EMOTE', 'SAY', 'ADMIN', 'ERROR']:
            label = QLabel(event_type)
            colors_group_layout.addWidget(label, row, 0)
            
            btn = QPushButton()
            btn.setMinimumSize(50, 25)
            btn.setMaximumHeight(25)
            btn.clicked.connect(lambda checked, et=event_type: self.change_color(et))
            self.color_buttons[event_type] = btn
            colors_group_layout.addWidget(btn, row, 1)
            row += 1
        
        colors_layout.addWidget(colors_group)
        
        # Цвета подсветки
        highlight_group = QGroupBox("Цвета подсветки строк")
        highlight_layout = QGridLayout(highlight_group)
        highlight_layout.setSpacing(2)
        highlight_layout.setContentsMargins(5, 5, 5, 5)
        highlight_layout.setVerticalSpacing(2)
        
        self.highlight_buttons = []
        for i in range(5):
            label = QLabel(f"Текст {i+1}")
            highlight_layout.addWidget(label, i, 0)
            
            btn = QPushButton()
            btn.setMinimumSize(50, 25)
            btn.setMaximumHeight(25)
            btn.clicked.connect(lambda checked, idx=i: self.change_highlight_color(idx))
            self.highlight_buttons.append(btn)
            highlight_layout.addWidget(btn, i, 1)
        
        colors_layout.addWidget(highlight_group)
        tabs.addTab(colors_tab, "Цвета")
        
        # Вкладка "Внешний вид"
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        appearance_layout.setSpacing(5)
        
        # Тема
        theme_group = QGroupBox("Тема оформления")
        theme_layout = QHBoxLayout(theme_group)
        theme_layout.setSpacing(5)
        theme_layout.setContentsMargins(5, 5, 5, 5)
        theme_layout.addWidget(QLabel("Тема:"))
        
        self.theme_combo = QComboBox()
        themes = ['Обычная', 'Пиратская', 'Тёмная', 'Uplink', 'Элизиум', 'Светло-серая', 'Тёмно-серая']
        self.theme_combo.addItems(themes)
        theme_layout.addWidget(self.theme_combo)
        appearance_layout.addWidget(theme_group)
        
        # Стиль таблицы
        table_group = QGroupBox("Стиль таблицы")
        table_layout = QHBoxLayout(table_group)
        table_layout.setSpacing(5)
        table_layout.setContentsMargins(5, 5, 5, 5)
        table_layout.addWidget(QLabel("Стиль:"))
        
        self.table_style_combo = QComboBox()
        self.table_style_combo.addItems(['Чередующиеся строки', 'Однотонный фон'])
        table_layout.addWidget(self.table_style_combo)
        appearance_layout.addWidget(table_group)
        
        # Цвет рабочей области
        workspace_group = QGroupBox("Цвет рабочей области")
        workspace_layout = QHBoxLayout(workspace_group)
        workspace_layout.setSpacing(5)
        workspace_layout.setContentsMargins(5, 5, 5, 5)
        workspace_layout.addWidget(QLabel("Цвет:"))
        
        self.workspace_btn = QPushButton()
        self.workspace_btn.setMinimumSize(50, 30)
        self.workspace_btn.clicked.connect(self.change_workspace_color)
        workspace_layout.addWidget(self.workspace_btn)
        appearance_layout.addWidget(workspace_group)
        
        # Шрифт
        font_group = QGroupBox("Шрифт")
        font_layout = QHBoxLayout(font_group)
        font_layout.setSpacing(5)
        font_layout.setContentsMargins(5, 5, 5, 5)
        
        self.font_btn = QPushButton("ШРИФТ")
        self.font_btn.clicked.connect(self.change_font)
        font_layout.addWidget(self.font_btn)
        
        self.font_label = QLabel("Consolas, 10pt")
        font_layout.addWidget(self.font_label)
        appearance_layout.addWidget(font_group)
        
        tabs.addTab(appearance_tab, "Внешний вид")
        
        layout.addWidget(tabs)
        
        # Кнопки
        buttons = QDialogButtonBox()
        ok_btn = buttons.addButton("ОК", QDialogButtonBox.AcceptRole)
        cancel_btn = buttons.addButton("Отмена", QDialogButtonBox.RejectRole)
        apply_btn = buttons.addButton("Применить", QDialogButtonBox.ApplyRole)
        
        buttons.accepted.connect(self.accept_settings)
        buttons.rejected.connect(self.reject)
        apply_btn.clicked.connect(self.apply_settings)
        layout.addWidget(buttons)
    
    def load_current_settings(self):
        if not self.parent_window:
            return
        
        # Загружаем цвета типов
        for event_type, btn in self.color_buttons.items():
            color = self.parent_window.colors.get(event_type, '#000000')
            btn.setStyleSheet(f"background-color: {color}")
        
        # Загружаем цвета подсветки
        for i, btn in enumerate(self.highlight_buttons):
            color = self.parent_window.highlight_colors[i]
            btn.setStyleSheet(f"background-color: {color}")
        
        # Загружаем тему
        theme_map = {
            'default': 'Обычная', 'pirate': 'Пиратская', 'dark': 'Тёмная',
            'uplink': 'Uplink', 'elysium': 'Элизиум', 
            'light_grey': 'Светло-серая', 'dark_grey': 'Тёмно-серая'
        }
        current_theme = theme_map.get(self.parent_window.current_theme, 'Обычная')
        self.theme_combo.setCurrentText(current_theme)
        
        # Загружаем стиль таблицы
        table_map = {'alternating': 'Чередующиеся строки', 'solid': 'Однотонный фон'}
        current_table = table_map.get(self.parent_window.table_style, 'Чередующиеся строки')
        self.table_style_combo.setCurrentText(current_table)
        
        # Загружаем цвет рабочей области
        self.workspace_btn.setStyleSheet(f"background-color: {self.parent_window.workspace_color}")
        
        # Загружаем шрифт
        font = self.parent_window.text_edit1.font()
        self.font_label.setText(f"{font.family()}, {font.pointSize()}pt")
    
    def change_color(self, event_type):
        current_color = self.parent_window.colors.get(event_type, '#000000')
        dialog = QColorDialog(QColor(current_color), self)
        dialog.setStyleSheet("QColorDialog, QColorDialog QLabel, QColorDialog QPushButton { color: #000000; background-color: #ffffff; }")
        if dialog.exec_() == QDialog.Accepted:
            color = dialog.currentColor()
            self.color_buttons[event_type].setStyleSheet(f"background-color: {color.name()}")
    
    def change_highlight_color(self, index):
        current_color = self.parent_window.highlight_colors[index]
        dialog = QColorDialog(QColor(current_color), self)
        dialog.setStyleSheet("QColorDialog, QColorDialog QLabel, QColorDialog QPushButton { color: #000000; background-color: #ffffff; }")
        if dialog.exec_() == QDialog.Accepted:
            color = dialog.currentColor()
            self.highlight_buttons[index].setStyleSheet(f"background-color: {color.name()}")
    
    def change_workspace_color(self):
        current_color = self.parent_window.workspace_color
        dialog = QColorDialog(QColor(current_color), self)
        dialog.setStyleSheet("QColorDialog, QColorDialog QLabel, QColorDialog QPushButton { color: #000000; background-color: #ffffff; }")
        if dialog.exec_() == QDialog.Accepted:
            color = dialog.currentColor()
            self.workspace_btn.setStyleSheet(f"background-color: {color.name()}")
    
    def change_font(self):
        current_font = self.parent_window.text_edit1.font()
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            self.font_label.setText(f"{font.family()}, {font.pointSize()}pt")
            self.current_font = font
    
    def apply_settings(self):
        if not self.parent_window:
            return
        
        # Применяем цвета типов
        for event_type, btn in self.color_buttons.items():
            color = btn.palette().button().color().name()
            self.parent_window.colors[event_type] = color
            if event_type in self.parent_window.filter_checkboxes:
                self.parent_window.filter_checkboxes[event_type].setStyleSheet(
                    f"QCheckBox {{ color: {color}; font-weight: bold; }}"
                )
        
        # Применяем цвета подсветки
        for i, btn in enumerate(self.highlight_buttons):
            color = btn.palette().button().color().name()
            self.parent_window.highlight_colors[i] = color
            if i < len(self.parent_window.highlight_edits):
                self.parent_window.highlight_edits[i].setStyleSheet(f"background-color: {color}; color: #000;")
        
        # Применяем тему
        theme_map = {
            'Обычная': 'default', 'Пиратская': 'pirate', 'Тёмная': 'dark',
            'Uplink': 'uplink', 'Элизиум': 'elysium',
            'Светло-серая': 'light_grey', 'Тёмно-серая': 'dark_grey'
        }
        theme_key = theme_map.get(self.theme_combo.currentText(), 'default')
        self.parent_window.current_theme = theme_key
        self.parent_window.apply_theme()
        
        # Применяем стиль таблицы
        table_map = {'Чередующиеся строки': 'alternating', 'Однотонный фон': 'solid'}
        table_key = table_map.get(self.table_style_combo.currentText(), 'alternating')
        self.parent_window.table_style = table_key
        self.parent_window.apply_table_style()
        
        # Применяем цвет рабочей области
        color = self.workspace_btn.palette().button().color().name()
        self.parent_window.workspace_color = color
        self.parent_window.apply_workspace_color()
        
        # Применяем шрифт
        if hasattr(self, 'current_font'):
            self.parent_window.text_edit1.setFont(self.current_font)
            self.parent_window.text_edit2.setFont(self.current_font)
            if hasattr(self.parent_window, 'table_widget'):
                self.parent_window.table_widget.setFont(self.current_font)
            if hasattr(self.parent_window, 'table_widget2'):
                self.parent_window.table_widget2.setFont(self.current_font)
        
        # Сохраняем настройки
        self.parent_window.save_settings()
        
        # Обновляем отображение
        if hasattr(self.parent_window, 'log_data') and self.parent_window.log_data:
            self.parent_window.display_log()
    
    def accept_settings(self):
        self.apply_settings()
        self.accept()