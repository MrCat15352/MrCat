#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления пустых ячеек после удаления шаблонов
"""

import re
from pathlib import Path

def fix_empty_cells(table_file):
    """Исправляет пустые ячейки в таблице"""
    print(f"Исправляем пустые ячейки в {table_file.name}...")
    
    with open(table_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем пустые ячейки на "N/A"
    content = re.sub(r'\|\s*\n\|', '|N/A\n|', content)
    
    # Убираем лишние пустые строки
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    with open(table_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Пустые ячейки исправлены!")

def main():
    table_file = Path("E:/GitRepo/MrCat/proverka/Таблицы/ОГРОМНАЯ_ТАБЛИЦА.txt")
    fix_empty_cells(table_file)

if __name__ == "__main__":
    main()