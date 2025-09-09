#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Универсальный скрипт для исправления отсутствующих реагентов в таблицах
Может удалять или заменять отсутствующие реагенты
"""

import os
import re
import argparse
from pathlib import Path

class ReagentFixer:
    def __init__(self, tables_path):
        self.tables_path = Path(tables_path)
        
        # Отсутствующие реагенты для удаления
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
        
        # Замены отсутствующих реагентов
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
    
    def remove_reagent_row(self, content, reagent_name):
        """Удаляет строку таблицы с указанным реагентом"""
        patterns = [
            # Обычный anchor паттерн
            rf'\|-\s*\n!\s*style="[^"]*"\s*\|\{{{{anchor\|[^}}]*{re.escape(reagent_name)}[^}}]*\}}}}[^\n]*\n(?:[^|]*\|[^\n]*\n)*',
            # Паттерн для строк без anchor
            rf'\|-\s*\n!\s*style="[^"]*"\s*\|[^|]*{re.escape(reagent_name)}[^|]*\n(?:[^|]*\|[^\n]*\n)*',
            # Паттерн для поврежденных anchor
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
    
    def replace_reagent_name(self, content, old_name, new_name):
        """Заменяет название реагента"""
        replacements_made = 0
        
        # Заменяем в anchor
        anchor_pattern = rf'\{{{{anchor\|[^}}]*{re.escape(old_name)}[^}}]*\}}}}'
        if re.search(anchor_pattern, content):
            content = re.sub(anchor_pattern, f'{{{{anchor|{new_name}}}}}', content)
            replacements_made += 1
        
        # Заменяем в названиях
        name_pattern = rf'\b{re.escape(old_name)}\b'
        if re.search(name_pattern, content):
            content = re.sub(name_pattern, new_name, content)
            replacements_made += 1
        
        return content, replacements_made
    
    def fix_table_file(self, table_file, action="remove"):
        """Исправляет файл таблицы"""
        print(f"Обрабатываем {table_file.name} (действие: {action})...")
        
        try:
            with open(table_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            with open(table_file, 'r', encoding='cp1251') as f:
                content = f.read()
        
        original_content = content
        total_changes = 0
        
        filename = table_file.name
        
        if action == "remove" and filename in self.missing_reagents:
            # Удаляем отсутствующие реагенты
            for missing_reagent in self.missing_reagents[filename]:
                content, removed = self.remove_reagent_row(content, missing_reagent)
                if removed > 0:
                    total_changes += removed
                    print(f"  Удалено {removed} строк с '{missing_reagent}'")
        
        elif action == "replace" and filename in self.replacements:
            # Заменяем отсутствующие реагенты
            for old_name, new_name in self.replacements[filename].items():
                content, replaced = self.replace_reagent_name(content, old_name, new_name)
                if replaced > 0:
                    total_changes += replaced
                    print(f"  Заменено '{old_name}' -> '{new_name}'")
        
        # Очищаем лишние пустые строки
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Сохраняем если были изменения
        if content != original_content:
            with open(table_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  OK: Выполнено {total_changes} изменений")
        else:
            print(f"  INFO: Изменений не требуется")
        
        return total_changes
    
    def fix_all_tables(self, action="remove"):
        """Исправляет все таблицы"""
        total_changes = 0
        
        action_name = "УДАЛЕНИЕ" if action == "remove" else "ЗАМЕНА"
        print(f"=== {action_name} ОТСУТСТВУЮЩИХ РЕАГЕНТОВ ===\n")
        
        target_files = ["Лекарства.txt", "Наркотики.txt", "Пиротехника.txt"]
        
        for filename in target_files:
            table_file = self.tables_path / filename
            if table_file.exists():
                changes = self.fix_table_file(table_file, action)
                total_changes += changes
            else:
                print(f"  WARNING: Файл {filename} не найден")
            print()
        
        return total_changes

def main():
    parser = argparse.ArgumentParser(description='Исправление отсутствующих реагентов в таблицах')
    parser.add_argument('--action', choices=['remove', 'replace'], default='remove',
                       help='Действие: remove (удалить) или replace (заменить)')
    parser.add_argument('--tables-path', default='E:/GitRepo/MrCat/proverka/Таблицы',
                       help='Путь к папке с таблицами')
    
    args = parser.parse_args()
    
    fixer = ReagentFixer(args.tables_path)
    
    print(f"=== ИСПРАВЛЕНИЕ ОТСУТСТВУЮЩИХ РЕАГЕНТОВ ===")
    print(f"Действие: {'Удаление' if args.action == 'remove' else 'Замена'}")
    print(f"Путь: {args.tables_path}\n")
    
    total_changes = fixer.fix_all_tables(args.action)
    
    print(f"=== ИТОГИ ===")
    print(f"Всего изменений: {total_changes}")
    print("Исправление завершено!")

if __name__ == "__main__":
    main()