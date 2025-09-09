#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенный скрипт для обновления таблиц реагентов
"""

import os
import re
import json
from pathlib import Path

class ReagentUpdater:
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
        
        # Ищем определения реагентов
        reagent_pattern = r'/datum/reagent/[^\s]*\s*\n((?:\t.*\n)*)'
        matches = re.findall(reagent_pattern, content)
        
        for reagent_body in matches:
            name_match = re.search(r'\tname\s*=\s*"([^"]+)"', reagent_body)
            desc_match = re.search(r'\tdescription\s*=\s*"([^"]+)"', reagent_body)
            color_match = re.search(r'\tcolor\s*=\s*"([^"]+)"', reagent_body)
            
            if name_match:
                reagent_name = name_match.group(1)
                self.reagents[reagent_name] = {
                    'description': desc_match.group(1) if desc_match else "",
                    'color': color_match.group(1) if color_match else "#FFFFFF",
                    'file': str(file_path)
                }
    
    def parse_all_recipes(self):
        """Парсит все рецепты"""
        recipe_dirs = [
            "code/modules/reagents/chemistry/recipes"
        ]
        
        for recipe_dir in recipe_dirs:
            full_dir = self.code_path / recipe_dir
            if full_dir.exists():
                for dm_file in full_dir.rglob("*.dm"):
                    self.parse_recipe_file(dm_file)
    
    def parse_recipe_file(self, file_path):
        """Парсит файл с рецептами"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            try:
                with open(file_path, 'r', encoding='cp1251') as f:
                    content = f.read()
            except:
                return
        
        # Ищем рецепты
        recipe_pattern = r'/datum/chemical_reaction/([^\s/]+)\s*\n((?:\t.*\n)*)'
        matches = re.findall(recipe_pattern, content)
        
        for recipe_name, recipe_body in matches:
            results_match = re.search(r'\tresults\s*=\s*list\(([^)]+)\)', recipe_body)
            required_match = re.search(r'\trequired_reagents\s*=\s*list\(([^)]+)\)', recipe_body)
            
            if results_match or required_match:
                self.recipes[recipe_name] = {
                    'results': results_match.group(1) if results_match else "",
                    'required': required_match.group(1) if required_match else "",
                    'file': str(file_path)
                }
    
    def extract_reagent_from_path(self, reagent_path):
        """Извлекает имя реагента из пути"""
        # /datum/reagent/consumable/ethanol -> ethanol
        # /datum/reagent/medicine/charcoal -> charcoal  
        parts = reagent_path.split('/')
        return parts[-1] if parts else reagent_path
    
    def find_recipe_for_reagent(self, reagent_name):
        """Находит рецепт для реагента"""
        for recipe_name, recipe_data in self.recipes.items():
            if reagent_name.lower() in recipe_data['results'].lower():
                return recipe_data
        return None
    
    def update_table_file(self, table_file):
        """Обновляет конкретный файл таблицы"""
        print(f"Обновляем {table_file.name}...")
        
        try:
            with open(table_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            with open(table_file, 'r', encoding='cp1251') as f:
                content = f.read()
        
        # Ищем строки таблицы с реагентами
        table_pattern = r'!\s*style="[^"]*"\s*\|\{\{anchor\|([^}]+)\}\}([^<\s]+)[^|]*\|([^|]*)\|([^|]*)\|-'
        matches = re.findall(table_pattern, content, re.DOTALL)
        
        updated_content = content
        updates_made = 0
        
        for anchor, name, formula, description in matches:
            clean_name = name.strip()
            
            # Ищем реагент в коде
            found_reagent = None
            for reagent_name, reagent_data in self.reagents.items():
                if reagent_name.lower() == clean_name.lower():
                    found_reagent = reagent_data
                    break
            
            if found_reagent and found_reagent['description']:
                # Обновляем описание
                old_desc = description.strip()
                new_desc = found_reagent['description']
                
                if old_desc != new_desc and new_desc:
                    pattern = re.escape(old_desc)
                    updated_content = re.sub(pattern, new_desc, updated_content, count=1)
                    updates_made += 1
                    print(f"  Обновлено описание для {clean_name}")
        
        # Сохраняем если были изменения
        if updates_made > 0:
            with open(table_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"  Сохранено {updates_made} обновлений")
        else:
            print(f"  Обновлений не требуется")
    
    def generate_detailed_report(self):
        """Генерирует детальный отчет"""
        self.parse_all_reagents()
        self.parse_all_recipes()
        
        report = f"""
=== ДЕТАЛЬНЫЙ ОТЧЕТ ПО РЕАГЕНТАМ ===

Найдено реагентов в коде: {len(self.reagents)}
Найдено рецептов в коде: {len(self.recipes)}

=== РЕАГЕНТЫ В КОДЕ ===
"""
        
        # Сортируем реагенты по алфавиту
        for name in sorted(self.reagents.keys()):
            reagent = self.reagents[name]
            report += f"- {name}: {reagent['description'][:50]}...\n"
        
        report += f"\n=== РЕЦЕПТЫ В КОДЕ ===\n"
        for name in sorted(self.recipes.keys()):
            recipe = self.recipes[name]
            report += f"- {name}: {recipe['required'][:50]}...\n"
        
        # Проверяем таблицы
        report += f"\n=== АНАЛИЗ ТАБЛИЦ ===\n"
        
        for table_file in self.tables_path.glob("*.txt"):
            report += f"\n--- {table_file.name} ---\n"
            
            try:
                with open(table_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                with open(table_file, 'r', encoding='cp1251') as f:
                    content = f.read()
            
            # Ищем реагенты в таблице
            table_pattern = r'\{\{anchor\|([^}]+)\}\}([^<\s]+)'
            table_reagents = re.findall(table_pattern, content)
            
            for anchor, name in table_reagents:
                clean_name = name.strip()
                found = False
                for reagent_name in self.reagents.keys():
                    if reagent_name.lower() == clean_name.lower():
                        found = True
                        break
                
                status = "✓ Найден" if found else "✗ Отсутствует"
                report += f"  {clean_name}: {status}\n"
        
        # Сохраняем отчет
        with open(self.code_path / "detailed_reagent_report.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("Детальный отчет сохранен в detailed_reagent_report.txt")
    
    def update_all_tables(self):
        """Обновляет все таблицы"""
        self.parse_all_reagents()
        self.parse_all_recipes()
        
        print(f"Загружено {len(self.reagents)} реагентов и {len(self.recipes)} рецептов")
        
        for table_file in self.tables_path.glob("*.txt"):
            self.update_table_file(table_file)

def main():
    code_path = "E:/GitRepo/MrCat"
    tables_path = "E:/GitRepo/MrCat/proverka/Таблицы"
    
    updater = ReagentUpdater(code_path, tables_path)
    
    print("Генерируем детальный отчет...")
    updater.generate_detailed_report()
    
    print("\nОбновляем таблицы...")
    updater.update_all_tables()
    
    print("\nГотово!")

if __name__ == "__main__":
    main()