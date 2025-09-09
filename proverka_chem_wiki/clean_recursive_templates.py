#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для удаления шаблонов {{RecursiveChem/...}} без рецептов из ОГРОМНАЯ_ТАБЛИЦА.txt
"""

import os
import re
from pathlib import Path

class RecursiveTemplatesCleaner:
    def __init__(self, code_path, table_file):
        self.code_path = Path(code_path)
        self.table_file = Path(table_file)
        self.recipes = set()
        
    def parse_all_recipes(self):
        """Парсит все рецепты из кода"""
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
        
        # Ищем результаты рецептов
        results_pattern = r'results\s*=\s*list\([^)]*"([^"]+)"'
        matches = re.findall(results_pattern, content)
        
        for match in matches:
            # Извлекаем имя реагента из пути
            reagent_name = match.split('/')[-1].replace('_', ' ')
            self.recipes.add(reagent_name)
    
    def clean_table(self):
        """Очищает таблицу от шаблонов без рецептов"""
        print(f"Загружаем рецепты из кода...")
        self.parse_all_recipes()
        print(f"Найдено {len(self.recipes)} рецептов")
        
        print(f"Обрабатываем {self.table_file.name}...")
        
        # Читаем файл построчно для экономии памяти
        with open(self.table_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        cleaned_lines = []
        removed_count = 0
        
        for line in lines:
            # Ищем шаблоны RecursiveChem
            template_pattern = r'\|\{\{RecursiveChem/([^}]+)\}\}'
            matches = re.findall(template_pattern, line)
            
            if matches:
                new_line = line
                for reagent_name in matches:
                    clean_name = reagent_name.replace('_', ' ')
                    
                    # Проверяем есть ли рецепт
                    has_recipe = any(clean_name.lower() in recipe.lower() or recipe.lower() in clean_name.lower() 
                                   for recipe in self.recipes)
                    
                    if not has_recipe:
                        # Удаляем шаблон
                        template = f"|{{{{RecursiveChem/{reagent_name}}}}}"
                        new_line = new_line.replace(template, "")
                        removed_count += 1
                        print(f"  Удален шаблон для {reagent_name}")
                
                cleaned_lines.append(new_line)
            else:
                cleaned_lines.append(line)
        
        # Сохраняем результат
        with open(self.table_file, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        
        print(f"Удалено {removed_count} шаблонов без рецептов")
        return removed_count

def main():
    code_path = "E:/GitRepo/MrCat"
    table_file = "E:/GitRepo/MrCat/proverka/Таблицы/ОГРОМНАЯ_ТАБЛИЦА.txt"
    
    cleaner = RecursiveTemplatesCleaner(code_path, table_file)
    
    print("=== ОЧИСТКА ШАБЛОНОВ RecursiveChem ===")
    removed = cleaner.clean_table()
    
    print(f"\n=== ИТОГИ ===")
    print(f"Удалено шаблонов: {removed}")
    print("Очистка завершена!")

if __name__ == "__main__":
    main()