#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
from pathlib import Path

def extract_reagent_info(file_path):
    """Извлекает информацию о реагентах из .dm файла"""
    reagents = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return reagents
    
    # Паттерн для поиска определений реагентов
    reagent_pattern = r'/datum/reagent/([^\s\n]+)'
    
    # Найти все определения реагентов
    reagent_matches = re.finditer(reagent_pattern, content)
    
    for match in reagent_matches:
        reagent_path = match.group(1)
        start_pos = match.start()
        
        # Найти конец определения реагента (следующий /datum или конец файла)
        next_datum = content.find('\n/datum/', start_pos + 1)
        if next_datum == -1:
            reagent_block = content[start_pos:]
        else:
            reagent_block = content[start_pos:next_datum]
        
        # Извлечь основную информацию
        reagent_info = {
            'path': f'/datum/reagent/{reagent_path}',
            'name': extract_property(reagent_block, 'name'),
            'description': extract_property(reagent_block, 'description'),
            'color': extract_property(reagent_block, 'color'),
            'taste_description': extract_property(reagent_block, 'taste_description'),
            'reagent_state': extract_property(reagent_block, 'reagent_state'),
            'metabolization_rate': extract_property(reagent_block, 'metabolization_rate'),
            'overdose_threshold': extract_property(reagent_block, 'overdose_threshold'),
            'addiction_threshold': extract_property(reagent_block, 'addiction_threshold'),
            'can_synth': extract_property(reagent_block, 'can_synth'),
            'harmful': extract_property(reagent_block, 'harmful'),
            'process_flags': extract_property(reagent_block, 'process_flags'),
            'file': file_path
        }
        
        # Только добавляем если есть имя
        if reagent_info['name']:
            reagents[reagent_info['name']] = reagent_info
    
    return reagents

def extract_property(block, property_name):
    """Извлекает значение свойства из блока кода"""
    pattern = rf'{property_name}\s*=\s*([^\n]+)'
    match = re.search(pattern, block)
    if match:
        value = match.group(1).strip()
        # Убираем комментарии
        if '//' in value:
            value = value.split('//')[0].strip()
        # Убираем кавычки
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        return value
    return None

def extract_recipe_info(file_path):
    """Извлекает информацию о рецептах из .dm файла"""
    recipes = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return recipes
    
    # Паттерн для поиска определений рецептов
    recipe_pattern = r'/datum/chemical_reaction/([^\s\n]+)'
    
    # Найти все определения рецептов
    recipe_matches = re.finditer(recipe_pattern, content)
    
    for match in recipe_matches:
        recipe_name = match.group(1)
        start_pos = match.start()
        
        # Найти конец определения рецепта
        next_datum = content.find('\n/datum/', start_pos + 1)
        if next_datum == -1:
            recipe_block = content[start_pos:]
        else:
            recipe_block = content[start_pos:next_datum]
        
        # Извлечь информацию о рецепте
        recipe_info = {
            'name': recipe_name,
            'results': extract_list_property(recipe_block, 'results'),
            'required_reagents': extract_list_property(recipe_block, 'required_reagents'),
            'required_catalysts': extract_list_property(recipe_block, 'required_catalysts'),
            'required_temp': extract_property(recipe_block, 'required_temp'),
            'file': file_path
        }
        
        recipes[recipe_name] = recipe_info
    
    return recipes

def extract_list_property(block, property_name):
    """Извлекает список из свойства (например, results, required_reagents)"""
    pattern = rf'{property_name}\s*=\s*list\(([^)]+)\)'
    match = re.search(pattern, block, re.DOTALL)
    if match:
        list_content = match.group(1)
        # Простая обработка списка - можно улучшить
        return list_content.strip()
    return None

def scan_chemistry_files():
    """Сканирует все файлы химии в проекте"""
    base_path = Path('E:/GitRepo/MrCat/code/modules/reagents/chemistry')
    
    all_reagents = {}
    all_recipes = {}
    
    # Сканируем файлы реагентов
    reagents_path = base_path / 'reagents'
    if reagents_path.exists():
        for file_path in reagents_path.rglob('*.dm'):
            print(f"Обрабатываю файл реагентов: {file_path}")
            reagents = extract_reagent_info(str(file_path))
            all_reagents.update(reagents)
    
    # Сканируем файлы рецептов
    recipes_path = base_path / 'recipes'
    if recipes_path.exists():
        for file_path in recipes_path.rglob('*.dm'):
            print(f"Обрабатываю файл рецептов: {file_path}")
            recipes = extract_recipe_info(str(file_path))
            all_recipes.update(recipes)
    
    return all_reagents, all_recipes

def generate_wiki_table(reagents, recipes):
    """Генерирует таблицу для вики"""
    
    # Сортируем реагенты по имени
    sorted_reagents = sorted(reagents.items(), key=lambda x: x[0])
    
    wiki_content = []
    wiki_content.append("== Химические компоненты ==")
    wiki_content.append("")
    wiki_content.append("{| class=\"wikitable sortable\"")
    wiki_content.append("! Название !! Формула !! Описание")
    
    for name, info in sorted_reagents:
        # Ищем рецепт для этого реагента
        formula = "—"
        for recipe_name, recipe_info in recipes.items():
            if recipe_info['results'] and name.lower() in recipe_info['results'].lower():
                if recipe_info['required_reagents']:
                    formula = recipe_info['required_reagents']
                break
        
        description = info.get('description', '—')
        if not description or description == 'None':
            description = "—"
        
        wiki_content.append("|-")
        wiki_content.append(f"| {name} || {formula} || {description}")
    
    wiki_content.append("|}")
    
    return "\n".join(wiki_content)

def main():
    print("Извлечение информации о химических компонентах...")
    
    # Извлекаем информацию из кода
    reagents, recipes = scan_chemistry_files()
    
    print(f"Найдено реагентов: {len(reagents)}")
    print(f"Найдено рецептов: {len(recipes)}")
    
    # Сохраняем в JSON для дальнейшего анализа
    with open('E:/GitRepo/MrCat/extracted_reagents.json', 'w', encoding='utf-8') as f:
        json.dump(reagents, f, ensure_ascii=False, indent=2)
    
    with open('E:/GitRepo/MrCat/extracted_recipes.json', 'w', encoding='utf-8') as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)
    
    # Генерируем таблицу для вики
    wiki_table = generate_wiki_table(reagents, recipes)
    
    with open('E:/GitRepo/MrCat/wiki_chemicals_table.txt', 'w', encoding='utf-8') as f:
        f.write(wiki_table)
    
    print("Готово! Файлы сохранены:")
    print("- extracted_reagents.json - все реагенты")
    print("- extracted_recipes.json - все рецепты")
    print("- wiki_chemicals_table.txt - таблица для вики")

if __name__ == "__main__":
    main()