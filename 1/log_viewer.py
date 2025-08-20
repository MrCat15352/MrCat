import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
from datetime import datetime

class LogViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SS13 Log Viewer")
        self.root.geometry("1200x800")

        # Цветовая схема для типов событий
        self.colors = {
            'ACCESS': '#4CAF50',    # Зеленый
            'GAME': '#2196F3',      # Синий
            'EMOTE': '#FF9800',     # Оранжевый
            'SAY': '#9C27B0',       # Фиолетовый
            'ADMIN': '#F44336',     # Красный
            'ERROR': '#FF0000',     # Ярко-красный
            'CRITICAL': '#8B0000'   # Темно-красный
        }

        self.setup_ui()
        self.log_data = []

    def setup_ui(self):
        # Панель управления
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill='x', padx=5, pady=5)

        # Кнопки
        ttk.Button(control_frame, text="Открыть лог", command=self.load_log).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Очистить", command=self.clear_log).pack(side='left', padx=5)

        # Поиск
        ttk.Label(control_frame, text="Поиск:").pack(side='left', padx=(20,5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.on_search)

        # Фильтры
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(filter_frame, text="Фильтры:").pack(side='left')

        # Чекбоксы для типов событий
        self.filter_vars = {}
        for event_type in self.colors.keys():
            var = tk.BooleanVar(value=True)
            self.filter_vars[event_type] = var
            cb = ttk.Checkbutton(filter_frame, text=event_type, variable=var, command=self.apply_filters)
            cb.pack(side='left', padx=5)

        # Критичные слова
        ttk.Label(filter_frame, text="Критичные:").pack(side='left', padx=(20,5))
        self.critical_var = tk.StringVar(value="ERROR,CRASH,FAIL,EXCEPTION")
        critical_entry = ttk.Entry(filter_frame, textvariable=self.critical_var, width=30)
        critical_entry.pack(side='left', padx=5)
        critical_entry.bind('<KeyRelease>', self.apply_filters)

        # Текстовое поле с прокруткой
        text_frame = ttk.Frame(self.root)
        text_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.text_widget = tk.Text(text_frame, wrap='none', font=('Consolas', 10))

        # Скроллбары
        v_scroll = ttk.Scrollbar(text_frame, orient='vertical', command=self.text_widget.yview)
        h_scroll = ttk.Scrollbar(text_frame, orient='horizontal', command=self.text_widget.xview)

        self.text_widget.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Размещение
        self.text_widget.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # Настройка тегов для подсветки
        for event_type, color in self.colors.items():
            self.text_widget.tag_configure(event_type, foreground=color, font=('Consolas', 10, 'bold'))

        self.text_widget.tag_configure('CRITICAL_HIGHLIGHT', background='#FFEB3B', foreground='#D32F2F')
        self.text_widget.tag_configure('SEARCH_HIGHLIGHT', background='#FFFF00')

    def load_log(self):
        file_path = filedialog.askopenfilename(
            title="Выберите лог файл",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.parse_log(content)
                self.display_log()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

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
                    # Строки без стандартного формата
                    self.log_data.append({
                        'timestamp': '',
                        'type': 'OTHER',
                        'message': line,
                        'full_line': line
                    })

    def display_log(self):
        self.text_widget.delete(1.0, tk.END)

        critical_words = [w.strip().upper() for w in self.critical_var.get().split(',') if w.strip()]

        for entry in self.log_data:
            if not self.filter_vars.get(entry['type'], tk.BooleanVar(value=True)).get():
                continue

            line = entry['full_line'] + '\n'
            start_pos = self.text_widget.index(tk.END + '-1c')
            self.text_widget.insert(tk.END, line)
            end_pos = self.text_widget.index(tk.END + '-1c')

            # Подсветка типа события
            if entry['type'] in self.colors:
                self.text_widget.tag_add(entry['type'], start_pos, end_pos)

            # Подсветка критичных слов
            for word in critical_words:
                if word in entry['message'].upper():
                    self.text_widget.tag_add('CRITICAL_HIGHLIGHT', start_pos, end_pos)
                    break

        self.apply_search_highlight()

    def apply_filters(self):
        self.display_log()

    def on_search(self, event=None):
        self.apply_search_highlight()

    def apply_search_highlight(self):
        # Удаляем предыдущую подсветку поиска
        self.text_widget.tag_remove('SEARCH_HIGHLIGHT', 1.0, tk.END)

        search_term = self.search_var.get()
        if not search_term:
            return

        # Поиск и подсветка
        start = 1.0
        while True:
            pos = self.text_widget.search(search_term, start, tk.END, nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(search_term)}c"
            self.text_widget.tag_add('SEARCH_HIGHLIGHT', pos, end)
            start = end

    def clear_log(self):
        self.text_widget.delete(1.0, tk.END)
        self.log_data = []

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = LogViewer()
    app.run()
