#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления новых реагентов из кода в таблицы
"""

import os
import re
from pathlib import Path

class MissingReagentsAdder:
    def __init__(self, code_path, tables_path):
        self.code_path = Path(code_path)
        self.tables_path = Path(tables_path)
        self.reagents = {}
        self.recipes = {}
        self.table_reagents = set()
        
    def parse_all_reagents(self):
        """Парсит все реагенты из кода"""
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
        
        reagent_pattern = r'/datum/reagent/([^\s]*)\s*\n((?:\t.*\n)*)'
        matches = re.findall(reagent_pattern, content)
        
        for reagent_path, reagent_body in matches:
            name_match = re.search(r'\tname\s*=\s*"([^"]+)"', reagent_body)
            desc_match = re.search(r'\tdescription\s*=\s*"([^"]+)"', reagent_body)
            color_match = re.search(r'\tcolor\s*=\s*"([^"]+)"', reagent_body)
            
            if name_match:
                reagent_name = name_match.group(1)
                # Определяем категорию по пути
                category = self.categorize_reagent(reagent_path, reagent_body)
                
                self.reagents[reagent_name] = {
                    'path': reagent_path,
                    'description': desc_match.group(1) if desc_match else "",
                    'color': color_match.group(1) if color_match else "#FFFFFF",
                    'category': category,
                    'file': str(file_path)
                }
    
    def categorize_reagent(self, reagent_path, reagent_body):
        """Определяет категорию реагента"""
        if 'medicine' in reagent_path:
            return 'medicine'
        elif 'drug' in reagent_path:
            return 'drug'
        elif 'toxin' in reagent_path:
            return 'toxin'
        elif 'pyrotechnic' in reagent_path:
            return 'pyrotechnic'
        elif 'other' in reagent_path:
            return 'component'
        else:
            # Анализируем содержимое
            if re.search(r'adjustBruteLoss|adjustFireLoss|adjustToxLoss|adjustOxyLoss', reagent_body):
                return 'medicine'
            elif re.search(r'addiction|overdose', reagent_body):
                return 'drug'
            elif re.search(r'explosion|fire|smoke', reagent_body):
                return 'pyrotechnic'
            elif re.search(r'toxin|poison', reagent_body):
                return 'toxin'
            else:
                return 'component'
    
    def parse_table_reagents(self):
        """Парсит существующие реагенты из таблиц"""
        for table_file in self.tables_path.glob("*.txt"):
            if table_file.name.startswith("Таблицы"):
                continue
                
            try:
                with open(table_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                with open(table_file, 'r', encoding='cp1251') as f:
                    content = f.read()
            
            # Ищем реагенты в таблице
            anchor_pattern = r'\{\{anchor\|([^}]+)\}\}([^<\s]+)'
            anchors = re.findall(anchor_pattern, content)
            
            for anchor, name in anchors:
                self.table_reagents.add(name.strip())
    
    def find_missing_reagents(self):
        """Находит реагенты, которые есть в коде, но нет в таблицах"""
        missing = {}
        
        for reagent_name, reagent_data in self.reagents.items():
            if reagent_name not in self.table_reagents:
                category = reagent_data['category']
                if category not in missing:
                    missing[category] = []
                missing[category].append((reagent_name, reagent_data))
        
        return missing
    
    def generate_table_entries(self, reagents_list, category):
        """Генерирует записи для таблицы"""
        entries = []
        
        for reagent_name, reagent_data in reagents_list:
            color = reagent_data['color']
            description = reagent_data['description']
            
            # Формируем запись для таблицы
            entry = f"""|-
! style="background-color:#FFEE88;" |{{{{anchor|{reagent_name}}}}}{reagent_name} <span style="color:{color};background-color:white">▮</span>
|{{{{RecursiveChem/{reagent_name}}}}}
|{description}
|0.2 units за тик
|N/A
|N/A"""
            
            entries.append(entry)
        
        return entries
    
    def add_to_table(self, table_file, new_entries):
        """Добавляет новые записи в таблицу"""
        try:
            with open(table_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            with open(table_file, 'r', encoding='cp1251') as f:
                content = f.read()
        
        # Находим конец таблицы
        table_end = content.rfind('|}')
        if table_end == -1:
            return False
        
        # Вставляем новые записи перед концом таблицы
        new_content = content[:table_end] + '\n'.join(new_entries) + '\n' + content[table_end:]
        
        with open(table_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    
    def process_missing_reagents(self):
        """Обрабатывает отсутствующие реагенты"""
        print("Анализируем реагенты...")
        self.parse_all_reagents()
        self.parse_table_reagents()
        
        print(f"Найдено {len(self.reagents)} реагентов в коде")
        print(f"Найдено {len(self.table_reagents)} реагентов в таблицах")
        
        missing = self.find_missing_reagents()
        
        # Маппинг категорий на файлы таблиц
        category_files = {
            'medicine': 'Лекарства.txt',
            'drug': 'Наркотики.txt',
            'pyrotechnic': 'Пиротехника.txt',
            'toxin': 'Токсины.txt',
            'component': 'Компоненты.txt'
        }
        
        total_added = 0
        
        for category, reagents_list in missing.items():
            if category in category_files:
                table_file = self.tables_path.parent / "proverka" / "Таблицы" / category_files[category]
                
                if table_file.exists():
                    print(f"\nДобавляем {len(reagents_list)} реагентов в {category_files[category]}:")
                    
                    # Показываем только первые 5 для краткости
                    for reagent_name, _ in reagents_list[:5]:
                        print(f"  + {reagent_name}")
                    
                    if len(reagents_list) > 5:
                        print(f"  ... и еще {len(reagents_list) - 5}")
                    
                    # Генерируем записи
                    entries = self.generate_table_entries(reagents_list, category)
                    
                    # Добавляем в таблицу
                    if self.add_to_table(table_file, entries):
                        total_added += len(reagents_list)
                        print(f"  OK: Добавлено {len(reagents_list)} записей")
                    else:
                        print(f"  ERROR: Ошибка добавления в {table_file}")
                else:
                    print(f"  WARNING: Файл {table_file} не найден")
        
        # Генерируем отчет
        report = f"""=== ОТЧЕТ О ДОБАВЛЕНИИ НОВЫХ РЕАГЕНТОВ ===

Всего реагентов в коде: {len(self.reagents)}
Реагентов в таблицах: {len(self.table_reagents)}
Добавлено новых реагентов: {total_added}

=== ДЕТАЛИЗАЦИЯ ПО КАТЕГОРИЯМ ===
"""
        
        for category, reagents_list in missing.items():
            report += f"\n{category.upper()}: {len(reagents_list)} реагентов\n"
            for reagent_name, reagent_data in reagents_list:
                report += f"  - {reagent_name}: {reagent_data['description'][:50]}...\n"
        
        with open(self.code_path / "proverka_chem_wiki" / "new_reagents_report.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        
        return total_added

def main():
    code_path = "E:/GitRepo/MrCat"
    tables_path = "E:/GitRepo/MrCat/proverka_chem_wiki"
    
    adder = MissingReagentsAdder(code_path, tables_path)
    
    print("=== ДОБАВЛЕНИЕ НОВЫХ РЕАГЕНТОВ ===")
    total_added = adder.process_missing_reagents()
    
    print(f"\n=== ИТОГИ ===")
    print(f"Всего добавлено реагентов: {total_added}")
    print("Отчет сохранен в new_reagents_report.txt")

if __name__ == "__main__":
    main()