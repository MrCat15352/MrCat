#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для удаления или замены отсутствующих реагентов в таблицах
"""

import os
import re
from pathlib import Path

class MissingReagentsCleaner:
    def __init__(self, tables_path):
        self.tables_path = Path(tables_path)
        
        # Список отсутствующих реагентов из отчета
        self.missing_reagents = {
            "Лекарства.txt": [
                "Seiver",
                "Skeleton's",
                "Pucetylline",
                "Chartreuse",
                "Restorative",
                "Medicated"
            ],
            "Наркотики.txt": [
                "Krokodil",
                "Bath"
            ],
            "Пиротехника.txt": [
                "Fluorosurfactant",
                "{{anchor|Smoke",
                "Explosion",
                "EMP",
                "Teslium"
            ]
        }
    
    def clean_table_file(self, table_file, missing_list):
        """Очищает файл таблицы от отсутствующих реагентов"""
        print(f"Обрабатываем {table_file.name}...")
        
        try:
            with open(table_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            with open(table_file, 'r', encoding='cp1251') as f:
                content = f.read()
        
        original_content = content
        removed_count = 0
        
        for missing_reagent in missing_list:
            # Ищем строки таблицы с отсутствующими реагентами
            # Паттерн для поиска строки таблицы начинающейся с реагента
            patterns = [
                # Обычный anchor паттерн
                rf'\|-\s*\n!\s*style="[^"]*"\s*\|\{{{{anchor\|[^}}]*{re.escape(missing_reagent)}[^}}]*\}}}}[^\n]*\n(?:[^|]*\|[^\n]*\n)*',
                # Паттерн для строк без anchor
                rf'\|-\s*\n!\s*style="[^"]*"\s*\|[^|]*{re.escape(missing_reagent)}[^|]*\n(?:[^|]*\|[^\n]*\n)*',
                # Паттерн для поврежденных anchor
                rf'\|-\s*\n!\s*style="[^"]*"\s*\|\{{{{anchor[^}}]*{re.escape(missing_reagent)}[^}}]*[^\n]*\n(?:[^|]*\|[^\n]*\n)*'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                if matches:
                    content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
                    removed_count += len(matches)
                    print(f"  Удалено {len(matches)} строк с '{missing_reagent}'")
                    break
        
        # Очищаем лишние пустые строки
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Сохраняем если были изменения
        if content != original_content:
            with open(table_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  OK: Удалено {removed_count} записей")
        else:
            print(f"  INFO: Изменений не требуется")
        
        return removed_count
    
    def clean_all_tables(self):
        """Очищает все таблицы от отсутствующих реагентов"""
        total_removed = 0
        
        print("=== УДАЛЕНИЕ ОТСУТСТВУЮЩИХ РЕАГЕНТОВ ===\n")
        
        for filename, missing_list in self.missing_reagents.items():
            table_file = self.tables_path / filename
            if table_file.exists():
                removed = self.clean_table_file(table_file, missing_list)
                total_removed += removed
            else:
                print(f"  WARNING: Файл {filename} не найден")
            print()
        
        return total_removed

def main():
    tables_path = "E:/GitRepo/MrCat/proverka/Таблицы"
    
    cleaner = MissingReagentsCleaner(tables_path)
    
    print("=== ОЧИСТКА ТАБЛИЦ ОТ ОТСУТСТВУЮЩИХ РЕАГЕНТОВ ===")
    total_removed = cleaner.clean_all_tables()
    
    print(f"=== ИТОГИ ===")
    print(f"Всего удалено записей: {total_removed}")
    print("Очистка завершена!")

if __name__ == "__main__":
    main()