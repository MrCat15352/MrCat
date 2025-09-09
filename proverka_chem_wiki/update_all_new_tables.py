#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновленный скрипт для работы со всеми таблицами включая новые
"""

import os
import re
from pathlib import Path

class NewTablesUpdater:
    def __init__(self, code_path, tables_path):
        self.code_path = Path(code_path)
        self.tables_path = Path(tables_path)
        self.reagents = {}
        self.recipes = {}
        
    def parse_all_reagents(self):
        """Парсит все файлы с реагентами"""
        reagent_dirs = [
            "code/modules/reagents/chemistry/reagents",
            "mod_celadon/food_and_drinks/code"
        ]
        
        for reagent_dir in reagent_dirs:
            full_dir = self.code_path / reagent_dir
            if full_dir.exists():
                for dm_file in full_dir.rglob("*.dm"):
                    self.parse_reagent_file(dm_file)
    
    def parse_reagent_file(self, file_path):
        """Парсит файл с реагентами"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            try:
                with open(file_path, 'r', encoding='cp1251') as f:
                    content = f.read()
            except:
                return
        
        reagent_pattern = r'/datum/reagent/[^\s]*\s*\n((?:\t.*\n)*)'
        matches = re.findall(reagent_pattern, content)
        
        for reagent_body in matches:
            name_match = re.search(r'\tname\s*=\s*"([^"]+)"', reagent_body)
            desc_match = re.search(r'\tdescription\s*=\s*"([^"]+)"', reagent_body)
            
            if name_match:
                reagent_name = name_match.group(1)
                self.reagents[reagent_name] = {
                    'description': desc_match.group(1) if desc_match else ""
                }
    
    def update_table_file(self, table_file):
        """Обновляет файл таблицы"""
        print(f"Обновляем {table_file.name}...")
        
        try:
            with open(table_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            with open(table_file, 'r', encoding='cp1251') as f:
                content = f.read()
        
        # Ищем anchor паттерны
        anchor_pattern = r'\{\{anchor\|([^}]+)\}\}([^<\s]+)'
        anchors = re.findall(anchor_pattern, content)
        
        updated_content = content
        updates_made = 0
        
        for anchor, name in anchors:
            clean_name = name.strip()
            
            # Ищем реагент в коде
            found_reagent = None
            if clean_name in self.reagents:
                found_reagent = self.reagents[clean_name]
            else:
                # Поиск по частичному совпадению
                for reagent_name, reagent_data in self.reagents.items():
                    if clean_name.lower() in reagent_name.lower() or reagent_name.lower() in clean_name.lower():
                        found_reagent = reagent_data
                        break
            
            if found_reagent and found_reagent['description']:
                # Ищем описание этого реагента в таблице
                row_pattern = r'\{\{anchor\|' + re.escape(anchor) + r'\}\}' + re.escape(name) + r'[^|]*\|[^|]*\|([^|]*?)(?=\|-|\|\})'
                row_match = re.search(row_pattern, content, re.DOTALL)
                
                if row_match:
                    old_desc = row_match.group(1).strip()
                    new_desc = found_reagent['description']
                    
                    if old_desc and new_desc and old_desc != new_desc and len(old_desc) > 20:
                        old_pattern = re.escape(old_desc)
                        updated_content = re.sub(old_pattern, new_desc, updated_content, count=1)
                        updates_made += 1
                        print(f"  Обновлено описание для {clean_name}")
        
        # Сохраняем если были изменения
        if updates_made > 0:
            with open(table_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"  OK: Сохранено {updates_made} обновлений")
        else:
            print(f"  INFO: Обновлений не требуется")
        
        return updates_made
    
    def update_all_tables(self):
        """Обновляет все таблицы"""
        print("Загружаем данные из кода...")
        self.parse_all_reagents()
        
        print(f"Загружено {len(self.reagents)} реагентов")
        
        total_updates = 0
        
        # Получаем все .txt файлы в папке таблиц
        table_files = list(self.tables_path.glob("*.txt"))
        
        print(f"\nОбновляем {len(table_files)} таблиц...")
        for table_file in table_files:
            updates = self.update_table_file(table_file)
            total_updates += updates
        
        return total_updates

def main():
    code_path = "E:/GitRepo/MrCat"
    tables_path = "E:/GitRepo/MrCat/proverka/Таблицы"
    
    updater = NewTablesUpdater(code_path, tables_path)
    
    print("=== ОБНОВЛЕНИЕ ВСЕХ ТАБЛИЦ РЕАГЕНТОВ ===")
    total_updates = updater.update_all_tables()
    
    print(f"\n=== ИТОГИ ===")
    print(f"Всего обновлений: {total_updates}")
    print("Обновление завершено!")

if __name__ == "__main__":
    main()