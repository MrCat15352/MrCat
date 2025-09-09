#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Продвинутый скрипт для замены отсутствующих реагентов альтернативными
"""

import os
import re
from pathlib import Path

class ReagentReplacer:
    def __init__(self, tables_path):
        self.tables_path = Path(tables_path)
        
        # Словарь замен: отсутствующий -> альтернативный
        self.replacements = {
            "Лекарства.txt": {
                "Skeleton's Boon": "Calcium",
                "Pucetylline Essence": "Charcoal", 
                "Chartreuse Solution": "Pentetic Acid",
                "Restorative Nanites": "Omnizine",
                "Medicated Suture": "Synthflesh"
            },
            "Наркотики.txt": {
                "Bath Salts": "Methamphetamine"
            },
            "Пиротехника.txt": {
                "Teslium Shock": "Teslium"
            }
        }
    
    def replace_in_table(self, table_file, replacements_dict):
        """Заменяет отсутствующие реагенты альтернативными"""
        print(f"Обрабатываем {table_file.name}...")
        
        try:
            with open(table_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            with open(table_file, 'r', encoding='cp1251') as f:
                content = f.read()
        
        original_content = content
        replacements_made = 0
        
        for missing_reagent, replacement in replacements_dict.items():
            # Заменяем в anchor
            anchor_pattern = rf'\{{{{anchor\|[^}}]*{re.escape(missing_reagent)}[^}}]*\}}}}'
            if re.search(anchor_pattern, content):
                content = re.sub(anchor_pattern, f'{{{{anchor|{replacement}}}}', content)
                replacements_made += 1
                print(f"  Заменен anchor '{missing_reagent}' -> '{replacement}'")
            
            # Заменяем в названиях
            name_pattern = rf'\b{re.escape(missing_reagent)}\b'
            if re.search(name_pattern, content):
                content = re.sub(name_pattern, replacement, content)
                replacements_made += 1
                print(f"  Заменено название '{missing_reagent}' -> '{replacement}'")
        
        # Сохраняем если были изменения
        if content != original_content:
            with open(table_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  OK: Выполнено {replacements_made} замен")
        else:
            print(f"  INFO: Замен не требуется")
        
        return replacements_made
    
    def process_all_tables(self):
        """Обрабатывает все таблицы"""
        total_replacements = 0
        
        print("=== ЗАМЕНА ОТСУТСТВУЮЩИХ РЕАГЕНТОВ ===\n")
        
        for filename, replacements_dict in self.replacements.items():
            table_file = self.tables_path / filename
            if table_file.exists():
                replaced = self.replace_in_table(table_file, replacements_dict)
                total_replacements += replaced
            else:
                print(f"  WARNING: Файл {filename} не найден")
            print()
        
        return total_replacements

def main():
    tables_path = "E:/GitRepo/MrCat/proverka/Таблицы"
    
    replacer = ReagentReplacer(tables_path)
    
    print("=== ЗАМЕНА ОТСУТСТВУЮЩИХ РЕАГЕНТОВ АЛЬТЕРНАТИВНЫМИ ===")
    total_replacements = replacer.process_all_tables()
    
    print(f"=== ИТОГИ ===")
    print(f"Всего выполнено замен: {total_replacements}")
    print("Замена завершена!")

if __name__ == "__main__":
    main()