#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки и обновления цветов реагентов в таблицах
"""

import os
import re
from pathlib import Path

class ReagentColorChecker:
    def __init__(self, code_path, tables_path):
        self.code_path = Path(code_path)
        self.tables_path = Path(tables_path)
        self.reagents = {}
        
    def parse_all_reagents(self):
        """Парсит все реагенты из кода с их цветами"""
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
            color_match = re.search(r'\tcolor\s*=\s*"([^"]+)"', reagent_body)
            
            if name_match:
                reagent_name = name_match.group(1)
                color = color_match.group(1) if color_match else "#FFFFFF"
                self.reagents[reagent_name] = color
    
    def check_table_colors(self, table_file):
        """Проверяет цвета в таблице"""
        try:
            with open(table_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            with open(table_file, 'r', encoding='cp1251') as f:
                content = f.read()
        
        # Ищем реагенты с цветами в таблице
        color_pattern = r'\{\{anchor\|([^}]+)\}\}([^<\s]+)[^<]*<span style="color:([^;]+);[^>]*>▮</span>'
        matches = re.findall(color_pattern, content)
        
        mismatches = []
        updates_made = 0
        updated_content = content
        
        for anchor, name, table_color in matches:
            clean_name = name.strip()
            
            if clean_name in self.reagents:
                code_color = self.reagents[clean_name]
                
                # Нормализуем цвета для сравнения
                table_color_norm = table_color.upper()
                code_color_norm = code_color.upper()
                
                if table_color_norm != code_color_norm:
                    mismatches.append({
                        'name': clean_name,
                        'table_color': table_color,
                        'code_color': code_color
                    })
                    
                    # Обновляем цвет в таблице
                    old_span = f'<span style="color:{table_color};background-color:white">▮</span>'
                    new_span = f'<span style="color:{code_color};background-color:white">▮</span>'
                    
                    if old_span in updated_content:
                        updated_content = updated_content.replace(old_span, new_span, 1)
                        updates_made += 1
        
        # Сохраняем обновленный файл
        if updates_made > 0:
            with open(table_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
        
        return mismatches, updates_made
    
    def check_all_tables(self):
        """Проверяет цвета во всех таблицах"""
        print("Загружаем цвета реагентов из кода...")
        self.parse_all_reagents()
        
        print(f"Найдено {len(self.reagents)} реагентов с цветами")
        
        total_mismatches = []
        total_updates = 0
        
        tables_dir = self.tables_path.parent / "proverka" / "Таблицы"
        
        for table_file in tables_dir.glob("*.txt"):
            print(f"\nПроверяем {table_file.name}...")
            
            mismatches, updates = self.check_table_colors(table_file)
            
            if mismatches:
                print(f"  Найдено {len(mismatches)} несоответствий цветов:")
                for mismatch in mismatches[:5]:  # Показываем первые 5
                    print(f"    {mismatch['name']}: {mismatch['table_color']} -> {mismatch['code_color']}")
                if len(mismatches) > 5:
                    print(f"    ... и еще {len(mismatches) - 5}")
                
                if updates > 0:
                    print(f"  OK: Обновлено {updates} цветов")
                    total_updates += updates
            else:
                print("  INFO: Все цвета соответствуют коду")
            
            total_mismatches.extend(mismatches)
        
        # Генерируем отчет
        report = f"""=== ОТЧЕТ О ПРОВЕРКЕ ЦВЕТОВ РЕАГЕНТОВ ===

Всего реагентов в коде: {len(self.reagents)}
Найдено несоответствий цветов: {len(total_mismatches)}
Обновлено цветов: {total_updates}

=== ДЕТАЛИЗАЦИЯ НЕСООТВЕТСТВИЙ ===
"""
        
        for mismatch in total_mismatches:
            report += f"{mismatch['name']}: {mismatch['table_color']} → {mismatch['code_color']}\n"
        
        with open(self.code_path / "proverka_chem_wiki" / "color_check_report.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        
        return len(total_mismatches), total_updates

def main():
    code_path = "E:/GitRepo/MrCat"
    tables_path = "E:/GitRepo/MrCat/proverka_chem_wiki"
    
    checker = ReagentColorChecker(code_path, tables_path)
    
    print("=== ПРОВЕРКА ЦВЕТОВ РЕАГЕНТОВ ===")
    mismatches, updates = checker.check_all_tables()
    
    print(f"\n=== ИТОГИ ===")
    print(f"Найдено несоответствий: {mismatches}")
    print(f"Обновлено цветов: {updates}")
    print("Отчет сохранен в color_check_report.txt")

if __name__ == "__main__":
    main()