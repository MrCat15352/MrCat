#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для обновления всех таблиц реагентов
"""

import os
import re
from pathlib import Path

class AllTablesUpdater:
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
            color_match = re.search(r'\tcolor\s*=\s*"([^"]+)"', reagent_body)
            
            if name_match:
                reagent_name = name_match.group(1)
                self.reagents[reagent_name] = {
                    'description': desc_match.group(1) if desc_match else "",
                    'color': color_match.group(1) if color_match else "#FFFFFF"
                }
    
    def parse_all_recipes(self):
        """Парсит все рецепты"""
        recipe_dirs = ["code/modules/reagents/chemistry/recipes"]
        
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
        
        recipe_pattern = r'/datum/chemical_reaction/([^\s/]+)\s*\n((?:\t.*\n)*)'
        matches = re.findall(recipe_pattern, content)
        
        for recipe_name, recipe_body in matches:
            results_match = re.search(r'\tresults\s*=\s*list\(([^)]+)\)', recipe_body)
            required_match = re.search(r'\trequired_reagents\s*=\s*list\(([^)]+)\)', recipe_body)
            
            if results_match or required_match:
                self.recipes[recipe_name] = {
                    'results': results_match.group(1) if results_match else "",
                    'required': required_match.group(1) if required_match else ""
                }
    
    def find_reagent_by_name(self, search_name):
        """Ищет реагент по имени"""
        # Прямое совпадение
        if search_name in self.reagents:
            return self.reagents[search_name]
        
        # Поиск по частичному совпадению
        for reagent_name, reagent_data in self.reagents.items():
            if search_name.lower() in reagent_name.lower() or reagent_name.lower() in search_name.lower():
                return reagent_data
        
        return None
    
    def extract_recipe_formula(self, reagent_name):
        """Извлекает формулу рецепта для реагента"""
        for recipe_name, recipe_data in self.recipes.items():
            if reagent_name.lower() in recipe_data['results'].lower():
                required = recipe_data['required']
                formula_parts = []
                
                # Парсим reagents и их количества
                reagent_matches = re.findall(r'/datum/reagent/([^=\s]+)\s*=\s*(\d+)', required)
                
                for reagent_path, amount in reagent_matches:
                    # Извлекаем имя реагента из пути
                    reagent_parts = reagent_path.split('/')
                    clean_name = reagent_parts[-1].replace('_', ' ').title()
                    formula_parts.append(f"{amount} part {clean_name}")
                
                return "<br>".join(formula_parts) if formula_parts else ""
        
        return ""
    
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
        table_pattern = r'(!\s*style="[^"]*"\s*\|\{\{anchor\|[^}]+\}\})([^<\s]+)([^|]*\|)([^|]*\|)([^|]*?)(\|-)'
        matches = re.findall(table_pattern, content, re.DOTALL)
        
        updated_content = content
        updates_made = 0
        
        for anchor_part, name, middle_part, formula_part, description_part, end_part in matches:
            clean_name = name.strip()
            
            # Ищем реагент в коде
            found_reagent = self.find_reagent_by_name(clean_name)
            
            if found_reagent:
                # Обновляем описание
                old_desc = description_part.strip()
                new_desc = found_reagent['description']
                
                if new_desc and old_desc != new_desc and len(old_desc) > 10:
                    # Заменяем описание
                    old_pattern = re.escape(old_desc)
                    updated_content = re.sub(old_pattern, new_desc, updated_content, count=1)
                    updates_made += 1
                    print(f"  Обновлено описание для {clean_name}")
                
                # Пытаемся найти и обновить формулу
                recipe_formula = self.extract_recipe_formula(clean_name)
                if recipe_formula and "RecursiveChem" in formula_part:
                    # Заменяем шаблон на реальную формулу
                    new_formula_part = f"|{recipe_formula}|"
                    old_formula_pattern = re.escape(formula_part)
                    updated_content = re.sub(old_formula_pattern, new_formula_part, updated_content, count=1)
                    updates_made += 1
                    print(f"  Обновлена формула для {clean_name}")
            else:
                print(f"  WARNING: Реагент {clean_name} не найден в коде")
        
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
        self.parse_all_recipes()
        
        print(f"Загружено {len(self.reagents)} реагентов и {len(self.recipes)} рецептов")
        
        total_updates = 0
        target_files = ["Лекарства.txt", "Наркотики.txt", "Пиротехника.txt", "Токсины.txt"]
        
        print("\nОбновляем таблицы...")
        for filename in target_files:
            table_file = self.tables_path / filename
            if table_file.exists():
                updates = self.update_table_file(table_file)
                total_updates += updates
            else:
                print(f"  WARNING: Файл {filename} не найден")
        
        return total_updates

def main():
    code_path = "E:/GitRepo/MrCat"
    tables_path = "E:/GitRepo/MrCat/proverka/Таблицы"
    
    updater = AllTablesUpdater(code_path, tables_path)
    
    print("=== ОБНОВЛЕНИЕ ВСЕХ ТАБЛИЦ РЕАГЕНТОВ ===")
    total_updates = updater.update_all_tables()
    
    print(f"\n=== ИТОГИ ===")
    print(f"Всего обновлений: {total_updates}")
    print("Обновление завершено!")

if __name__ == "__main__":
    main()