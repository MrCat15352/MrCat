#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для обновления таблиц реагентов на основе актуального кода игры
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
        
    def parse_reagent_files(self):
        """Парсит файлы с реагентами из кода"""
        reagent_files = [
            "code/modules/reagents/chemistry/reagents/other_reagents.dm",
            "code/modules/reagents/chemistry/reagents/medicine_reagents.dm",
            "code/modules/reagents/chemistry/reagents/toxin_reagents.dm",
            "code/modules/reagents/chemistry/reagents/drug_reagents.dm",
            "code/modules/reagents/chemistry/reagents/pyrotechnic_reagents.dm"
        ]
        
        for file_path in reagent_files:
            full_path = self.code_path / file_path
            if full_path.exists():
                self.parse_reagent_file(full_path)
    
    def parse_reagent_file(self, file_path):
        """Парсит отдельный файл с реагентами"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            with open(file_path, 'r', encoding='cp1251') as f:
                content = f.read()
        
        # Ищем определения реагентов
        reagent_pattern = r'/datum/reagent/([^\s]+)\s*\n([^/]*?)(?=\n/datum/reagent/|\n/datum/|\Z)'
        matches = re.findall(reagent_pattern, content, re.MULTILINE | re.DOTALL)
        
        for reagent_path, reagent_body in matches:
            name_match = re.search(r'name\s*=\s*"([^"]+)"', reagent_body)
            desc_match = re.search(r'description\s*=\s*"([^"]+)"', reagent_body)
            color_match = re.search(r'color\s*=\s*"([^"]+)"', reagent_body)
            
            if name_match:
                reagent_name = name_match.group(1)
                self.reagents[reagent_name] = {
                    'path': reagent_path,
                    'description': desc_match.group(1) if desc_match else "",
                    'color': color_match.group(1) if color_match else "#FFFFFF"
                }
    
    def parse_recipe_files(self):
        """Парсит файлы с рецептами"""
        recipe_files = [
            "code/modules/reagents/chemistry/recipes/others.dm",
            "code/modules/reagents/chemistry/recipes/medicine.dm",
            "code/modules/reagents/chemistry/recipes/toxins.dm",
            "code/modules/reagents/chemistry/recipes/drugs.dm",
            "code/modules/reagents/chemistry/recipes/pyrotechnics.dm"
        ]
        
        for file_path in recipe_files:
            full_path = self.code_path / file_path
            if full_path.exists():
                self.parse_recipe_file(full_path)
    
    def parse_recipe_file(self, file_path):
        """Парсит отдельный файл с рецептами"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            with open(file_path, 'r', encoding='cp1251') as f:
                content = f.read()
        
        # Ищем рецепты
        recipe_pattern = r'/datum/chemical_reaction/([^\s]+)\s*\n([^/]*?)(?=\n/datum/chemical_reaction/|\n/datum/|\Z)'
        matches = re.findall(recipe_pattern, content, re.MULTILINE | re.DOTALL)
        
        for recipe_name, recipe_body in matches:
            results_match = re.search(r'results\s*=\s*list\(([^)]+)\)', recipe_body)
            required_match = re.search(r'required_reagents\s*=\s*list\(([^)]+)\)', recipe_body)
            
            if results_match and required_match:
                self.recipes[recipe_name] = {
                    'results': results_match.group(1),
                    'required': required_match.group(1)
                }
    
    def update_components_table(self):
        """Обновляет таблицу компонентов"""
        components_file = self.tables_path / "Компоненты.txt"
        if not components_file.exists():
            return
        
        # Читаем текущую таблицу
        with open(components_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Список компонентов из изображения
        components_to_check = [
            "Ash", "Oil", "Phenol", "Acetone", "Sodium Chloride", 
            "Ammonia", "Diethylamine", "Saltpetre", "Lye", 
            "Hydrogen Peroxide", "Pentaerythritol", "Acetaldehyde", 
            "Acetone Oxide", "Wittel"
        ]
        
        updated_content = content
        
        for component in components_to_check:
            if component in self.reagents:
                reagent_info = self.reagents[component]
                # Обновляем описание если найдено в коде
                if reagent_info['description']:
                    # Ищем строку с описанием компонента и обновляем
                    pattern = rf'(\|\s*{re.escape(component)}[^|]*\|[^|]*\|)([^|]*?)(\|-)'
                    match = re.search(pattern, updated_content, re.DOTALL)
                    if match:
                        new_desc = reagent_info['description']
                        updated_content = updated_content.replace(match.group(2), new_desc)
        
        # Сохраняем обновленную таблицу
        with open(components_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"Обновлена таблица: {components_file}")
    
    def check_reagent_existence(self):
        """Проверяет существование реагентов из таблиц в коде"""
        missing_reagents = []
        
        for table_file in self.tables_path.glob("*.txt"):
            with open(table_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем названия реагентов в таблицах
            reagent_names = re.findall(r'\{\{anchor\|([^}]+)\}\}([^<\s]+)', content)
            
            for anchor, name in reagent_names:
                clean_name = name.strip()
                if clean_name not in self.reagents:
                    missing_reagents.append((table_file.name, clean_name))
        
        return missing_reagents
    
    def generate_report(self):
        """Генерирует отчет о состоянии реагентов"""
        self.parse_reagent_files()
        self.parse_recipe_files()
        
        missing = self.check_reagent_existence()
        
        report = f"""
=== ОТЧЕТ ПО ОБНОВЛЕНИЮ РЕАГЕНТОВ ===

Найдено реагентов в коде: {len(self.reagents)}
Найдено рецептов в коде: {len(self.recipes)}

Отсутствующие в коде реагенты:
"""
        
        for table_name, reagent_name in missing:
            report += f"- {reagent_name} (из таблицы {table_name})\n"
        
        # Сохраняем отчет
        with open(self.code_path / "reagent_update_report.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("Отчет сохранен в reagent_update_report.txt")
        return missing

def main():
    code_path = "E:/GitRepo/MrCat"
    tables_path = "E:/GitRepo/MrCat/proverka/Таблицы"
    
    updater = ReagentUpdater(code_path, tables_path)
    
    print("Анализируем реагенты...")
    missing_reagents = updater.generate_report()
    
    print(f"\nНайдено {len(missing_reagents)} отсутствующих реагентов")
    
    # Обновляем таблицы
    print("Обновляем таблицы...")
    updater.update_components_table()
    
    print("Готово!")

if __name__ == "__main__":
    main()