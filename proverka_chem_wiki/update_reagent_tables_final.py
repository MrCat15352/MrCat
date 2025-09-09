#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный скрипт для обновления таблиц реагентов
"""

import os
import re
import json
from pathlib import Path

class ReagentTableUpdater:
    def __init__(self, code_path, tables_path):
        self.code_path = Path(code_path)
        self.tables_path = Path(tables_path)
        self.reagents = {}
        self.recipes = {}
        
        # Маппинг старых названий на новые
        self.name_mapping = {
            "Libital": "Bicaridine",
            "Styptic Powder": "Styptic powder", 
            "Helbital": "Kelotane",
            "Saline-Glucose Solution": "Saline-Glucose solution",
            "Tetracordrazine": "Tricordrazine",
            "Salicylic Acid": "Salicylic acid",
            "Pentetic Acid": "Pentetic acid",
            "System Cleaner": "System cleaner",
            "Liquid Solder": "Liquid solder",
            "Miner's Salve": "Miner's salve",
            "Strange Reagent": "Strange reagent",
            "Regenerative Jelly": "Regenerative jelly",
            "C4L-Z1UM Agent": "C4L-Z1UM agent",
            "Skeleton's Boon": "Skeleton's boon",
            "Soulus Dust": "Soulus dust",
            "Purified Soulus Dust": "Purified soulus dust",
            "Fervor Ignium": "Fervor ignium",
            "Restorative Nanites": "Restorative nanites",
            "Medicated Suture": "Medicated suture",
            "Advanced Regenerative Mesh": "Advanced regenerative mesh",
            "Ashen Fibers": "Ashen fibers",
            "Burn Medicine": "Burn medicine",
            "Bath Salts": "Bath salts",
            "Stabilizing Agent": "Stabilizing agent",
            "Smoke Powder": "Smoke powder",
            "Flash Powder": "Flash powder",
            "Sonic Powder": "Sonic powder",
            "Liquid Dark Matter": "Liquid dark matter",
            "EMP Powder": "EMP powder",
            "Explosion Powder": "Explosion powder",
            "Holy Water": "Holy water",
            "Sulphuric Acid": "Sulphuric acid",
            "Fluorosulfuric Acid": "Fluorosulfuric acid",
            "Nitric Acid": "Nitric acid",
            "Unstable Mutagen": "Unstable mutagen",
            "Hydrogen Peroxide": "Hydrogen peroxide",
            "Acetone Oxide": "Acetone oxide"
        }
        
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
    
    def find_reagent_by_name(self, search_name):
        """Ищет реагент по имени с учетом маппинга"""
        # Сначала проверяем прямое совпадение
        if search_name in self.reagents:
            return self.reagents[search_name]
        
        # Проверяем маппинг
        if search_name in self.name_mapping:
            mapped_name = self.name_mapping[search_name]
            if mapped_name in self.reagents:
                return self.reagents[mapped_name]
        
        # Ищем по частичному совпадению
        for reagent_name, reagent_data in self.reagents.items():
            if search_name.lower() in reagent_name.lower() or reagent_name.lower() in search_name.lower():
                return reagent_data
        
        return None
    
    def extract_recipe_formula(self, reagent_name):
        """Извлекает формулу рецепта для реагента"""
        for recipe_name, recipe_data in self.recipes.items():
            if reagent_name.lower() in recipe_data['results'].lower():
                # Парсим required_reagents
                required = recipe_data['required']
                # Упрощаем формулу
                formula_parts = []
                reagent_matches = re.findall(r'/datum/reagent/[^=]+ = (\d+)', required)
                reagent_names = re.findall(r'/datum/reagent/([^/\s=]+)', required)
                
                for i, name in enumerate(reagent_names):
                    amount = reagent_matches[i] if i < len(reagent_matches) else "1"
                    clean_name = name.replace('_', ' ').title()
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
        table_pattern = r'(!\s*style="[^"]*"\s*\|\{\{anchor\|[^}]+\}\})([^<\s]+)([^|]*\|)([^|]*\|)([^|]*)\|-'
        matches = re.findall(table_pattern, content, re.DOTALL)
        
        updated_content = content
        updates_made = 0
        
        for anchor_part, name, middle_part, formula_part, description_part in matches:
            clean_name = name.strip()
            
            # Ищем реагент в коде
            found_reagent = self.find_reagent_by_name(clean_name)
            
            if found_reagent:
                # Обновляем описание
                old_desc = description_part.strip()
                new_desc = found_reagent['description']
                
                if new_desc and old_desc != new_desc:
                    # Заменяем описание
                    old_pattern = re.escape(old_desc)
                    updated_content = re.sub(old_pattern, new_desc, updated_content, count=1)
                    updates_made += 1
                    print(f"  Обновлено описание для {clean_name}")
                
                # Пытаемся найти и обновить формулу
                recipe_formula = self.extract_recipe_formula(clean_name)
                if recipe_formula:
                    # Ищем текущую формулу в таблице
                    current_formula = formula_part.strip('|').strip()
                    if current_formula and "RecursiveChem" in current_formula:
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
    
    def create_missing_reagents_report(self):
        """Создает отчет об отсутствующих реагентах"""
        missing_reagents = []
        
        for table_file in self.tables_path.glob("*.txt"):
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
                found_reagent = self.find_reagent_by_name(clean_name)
                
                if not found_reagent:
                    missing_reagents.append({
                        'table': table_file.name,
                        'name': clean_name,
                        'anchor': anchor
                    })
        
        # Сохраняем отчет
        report = "=== ОТСУТСТВУЮЩИЕ РЕАГЕНТЫ ===\n\n"
        
        by_table = {}
        for reagent in missing_reagents:
            table = reagent['table']
            if table not in by_table:
                by_table[table] = []
            by_table[table].append(reagent)
        
        for table, reagents in by_table.items():
            report += f"--- {table} ---\n"
            for reagent in reagents:
                report += f"- {reagent['name']} (anchor: {reagent['anchor']})\n"
            report += "\n"
        
        with open(self.code_path / "missing_reagents_report.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Отчет об отсутствующих реагентах сохранен: {len(missing_reagents)} реагентов")
        return missing_reagents
    
    def update_all_tables(self):
        """Обновляет все таблицы"""
        print("Загружаем данные из кода...")
        self.parse_all_reagents()
        self.parse_all_recipes()
        
        print(f"Загружено {len(self.reagents)} реагентов и {len(self.recipes)} рецептов")
        
        print("\nОбновляем таблицы...")
        for table_file in self.tables_path.glob("*.txt"):
            self.update_table_file(table_file)
        
        print("\nСоздаем отчет об отсутствующих реагентах...")
        missing = self.create_missing_reagents_report()
        
        return len(missing)

def main():
    code_path = "E:/GitRepo/MrCat"
    tables_path = "E:/GitRepo/MrCat/proverka/Таблицы"
    
    updater = ReagentTableUpdater(code_path, tables_path)
    
    print("=== ОБНОВЛЕНИЕ ТАБЛИЦ РЕАГЕНТОВ ===")
    missing_count = updater.update_all_tables()
    
    print(f"\n=== ИТОГИ ===")
    print(f"Найдено отсутствующих реагентов: {missing_count}")
    print("Все таблицы обновлены!")
    print("\nПроверьте файлы:")
    print("- missing_reagents_report.txt - отчет об отсутствующих реагентах")
    print("- Обновленные таблицы в папке proverka/Таблицы/")

if __name__ == "__main__":
    main()