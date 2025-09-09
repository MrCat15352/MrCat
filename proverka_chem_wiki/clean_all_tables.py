#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для очистки всех таблиц от отсутствующих реагентов
"""

import os
import re
from pathlib import Path

class AllTablesCleaner:
    def __init__(self, tables_path):
        self.tables_path = Path(tables_path)
        
        # Все отсутствующие реагенты
        self.missing_reagents = [
            "Seiver", "Skeleton's", "Pucetylline", "Chartreuse", 
            "Restorative", "Medicated", "Krokodil", "Bath", 
            "Fluorosurfactant", "{{anchor|Smoke", "Explosion", 
            "EMP", "Teslium"
        ]
    
    def remove_reagent_row(self, content, reagent_name):
        """Удаляет строку таблицы с указанным реагентом"""
        patterns = [
            rf'\|-\s*\n!\s*style="[^"]*"\s*\|\{{{{anchor\|[^}}]*{re.escape(reagent_name)}[^}}]*\}}}}[^\n]*\n(?:[^|]*\|[^\n]*\n)*',
            rf'\|-\s*\n!\s*style="[^"]*"\s*\|[^|]*{re.escape(reagent_name)}[^|]*\n(?:[^|]*\|[^\n]*\n)*',
            rf'\|-\s*\n!\s*style="[^"]*"\s*\|\{{{{anchor[^}}]*{re.escape(reagent_name)}[^}}]*[^\n]*\n(?:[^|]*\|[^\n]*\n)*'
        ]
        
        removed_count = 0
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            if matches:
                content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
                removed_count += len(matches)
                break
        
        return content, removed_count
    
    def clean_table_file(self, table_file):
        """Очищает файл таблицы"""
        print(f"Обрабатываем {table_file.name}...")
        
        try:
            with open(table_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            with open(table_file, 'r', encoding='cp1251') as f:
                content = f.read()
        
        original_content = content
        total_removed = 0
        
        for missing_reagent in self.missing_reagents:
            content, removed = self.remove_reagent_row(content, missing_reagent)
            if removed > 0:
                total_removed += removed
                print(f"  Удалено {removed} строк с '{missing_reagent}'")
        
        # Очищаем лишние пустые строки
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Сохраняем если были изменения
        if content != original_content:
            with open(table_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  OK: Удалено {total_removed} записей")
        else:
            print(f"  INFO: Изменений не требуется")
        
        return total_removed
    
    def clean_all_tables(self):
        """Очищает все таблицы"""
        print("=== ОЧИСТКА ВСЕХ ТАБЛИЦ ОТ ОТСУТСТВУЮЩИХ РЕАГЕНТОВ ===\n")
        
        total_removed = 0
        table_files = list(self.tables_path.glob("*.txt"))
        
        for table_file in table_files:
            removed = self.clean_table_file(table_file)
            total_removed += removed
            print()
        
        return total_removed

def main():
    tables_path = "E:/GitRepo/MrCat/proverka/Таблицы"
    
    cleaner = AllTablesCleaner(tables_path)
    
    total_removed = cleaner.clean_all_tables()
    
    print(f"=== ИТОГИ ===")
    print(f"Всего удалено записей: {total_removed}")
    print("Очистка завершена!")

if __name__ == "__main__":
    main()