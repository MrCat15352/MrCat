#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re

def clean_formula(formula):
    """Очищает формулу от лишних символов"""
    if not formula or formula == "—":
        return "—"
    
    # Убираем /datum/reagent/ префиксы
    formula = re.sub(r'/datum/reagent/[^=\s,]+', lambda m: m.group(0).split('/')[-1], formula)
    
    # Упрощаем формулу
    formula = formula.replace('consumable/', '').replace('medicine/', '').replace('toxin/', '')
    
    return formula

def create_improved_wiki_table():
    """Создает улучшенную таблицу для вики"""
    
    # Загружаем данные
    with open('E:/GitRepo/MrCat/extracted_reagents.json', 'r', encoding='utf-8') as f:
        reagents = json.load(f)
    
    with open('E:/GitRepo/MrCat/extracted_recipes.json', 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    # Создаем словарь рецептов по результатам
    recipe_map = {}
    for recipe_name, recipe_info in recipes.items():
        if recipe_info.get('results'):
            results = recipe_info['results']
            # Извлекаем названия реагентов из результатов
            result_matches = re.findall(r'/datum/reagent/[^=\s,]+', results)
            for match in result_matches:
                reagent_name = match.split('/')[-1]
                if reagent_name not in recipe_map:
                    recipe_map[reagent_name] = []
                recipe_map[reagent_name].append(recipe_info.get('required_reagents', '—'))
    
    # Категории для группировки
    categories = {
        'Основные элементы': ['water', 'oxygen', 'hydrogen', 'nitrogen', 'carbon', 'iron', 'sodium', 'chlorine', 'sulfur', 'phosphorus'],
        'Медицинские препараты': [],
        'Токсины и яды': [],
        'Алкогольные напитки': [],
        'Еда и напитки': [],
        'Наркотики': [],
        'Прочие химикаты': []
    }
    
    # Сортируем реагенты по категориям
    categorized_reagents = {cat: [] for cat in categories.keys()}
    
    for name, info in reagents.items():
        reagent_path = info.get('path', '').lower()
        
        if any(elem in name.lower() for elem in categories['Основные элементы']):
            categorized_reagents['Основные элементы'].append((name, info))
        elif 'medicine' in reagent_path or any(med in name.lower() for med in ['bicaridine', 'kelotane', 'antitoxin', 'tricordrazine', 'omnizine']):
            categorized_reagents['Медицинские препараты'].append((name, info))
        elif 'toxin' in reagent_path or 'poison' in name.lower() or 'toxic' in info.get('description', '').lower():
            categorized_reagents['Токсины и яды'].append((name, info))
        elif 'ethanol' in reagent_path or 'alcohol' in reagent_path or any(drink in name.lower() for drink in ['beer', 'wine', 'vodka', 'whiskey', 'rum']):
            categorized_reagents['Алкогольные напитки'].append((name, info))
        elif 'consumable' in reagent_path or 'food' in reagent_path or 'juice' in name.lower():
            categorized_reagents['Еда и напитки'].append((name, info))
        elif 'drug' in reagent_path or any(drug in name.lower() for drug in ['space_drugs', 'crank', 'meth']):
            categorized_reagents['Наркотики'].append((name, info))
        else:
            categorized_reagents['Прочие химикаты'].append((name, info))
    
    # Генерируем таблицу
    wiki_content = []
    wiki_content.append("== Химические компоненты ==")
    wiki_content.append("")
    
    for category, reagent_list in categorized_reagents.items():
        if not reagent_list:
            continue
            
        wiki_content.append(f"=== {category} ===")
        wiki_content.append("")
        wiki_content.append("{| class=\"wikitable sortable\"")
        wiki_content.append("! Название !! Формула !! Описание !! Цвет")
        
        # Сортируем по алфавиту
        reagent_list.sort(key=lambda x: x[0])
        
        for name, info in reagent_list:
            # Ищем рецепт
            formula = "—"
            reagent_key = info.get('path', '').split('/')[-1] if info.get('path') else name.lower().replace(' ', '_')
            
            if reagent_key in recipe_map and recipe_map[reagent_key]:
                formula = clean_formula(recipe_map[reagent_key][0])
            
            description = info.get('description', '—')
            if not description or description == 'None':
                description = "—"
            
            color = info.get('color', '—')
            if not color or color == 'None':
                color = "—"
            
            wiki_content.append("|-")
            wiki_content.append(f"| {name} || {formula} || {description} || {color}")
        
        wiki_content.append("|}")
        wiki_content.append("")
    
    return "\n".join(wiki_content)

def main():
    print("Создание улучшенной таблицы для вики...")
    
    wiki_table = create_improved_wiki_table()
    
    with open('E:/GitRepo/MrCat/improved_wiki_table.txt', 'w', encoding='utf-8') as f:
        f.write(wiki_table)
    
    print("Улучшенная таблица сохранена в improved_wiki_table.txt")

if __name__ == "__main__":
    main()