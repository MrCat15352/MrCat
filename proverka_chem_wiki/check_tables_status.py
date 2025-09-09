#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки состояния таблиц после очистки от отсутствующих реагентов
"""

import os
import re
from pathlib import Path

class TablesStatusChecker:
    def __init__(self, tables_path):
        self.tables_path = Path(tables_path)
        
        # Список всех потенциально проблемных реагентов
        self.problematic_reagents = [
            "Seiver", "Skeleton's", "Pucetylline", "Chartreuse", "Restorative", "Medicated",
            "Krokodil", "Bath", "Fluorosurfactant", "{{anchor|Smoke", "Explosion", "EMP", "Teslium"
        ]
    
    def check_table_file(self, table_file):
        """Проверяет файл таблицы на наличие проблемных реагентов"""
        print(f"Проверяем {table_file.name}...")
        
        try:
            with open(table_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            with open(table_file, 'r', encoding='cp1251') as f:
                content = f.read()
        
        # Подсчитываем общее количество реагентов
        reagent_rows = re.findall(r'\|-\s*\n!\s*style="[^"]*"\s*\|', content)
        total_reagents = len(reagent_rows)
        
        # Ищем проблемные реагенты
        found_problems = []
        for reagent in self.problematic_reagents:
            if reagent in content:
                found_problems.append(reagent)
        
        # Ищем пустые строки таблицы
        empty_rows = re.findall(r'\|-\s*\n!\s*style="[^"]*"\s*\|\s*\n', content)
        
        print(f"  Всего реагентов: {total_reagents}")
        
        if found_problems:
            print(f"  ПРОБЛЕМЫ: Найдены отсутствующие реагенты: {', '.join(found_problems)}")
        
        if empty_rows:
            print(f"  ПРОБЛЕМЫ: Найдены пустые строки: {len(empty_rows)}")
        
        if not found_problems and not empty_rows:
            print(f"  OK: Проблем не найдено")
        
        return {
            'total_reagents': total_reagents,
            'problems': found_problems,
            'empty_rows': len(empty_rows)
        }
    
    def check_all_tables(self):
        """Проверяет все таблицы"""
        print("=== ПРОВЕРКА СОСТОЯНИЯ ТАБЛИЦ ===\n")
        
        # Получаем все .txt файлы в папке таблиц
        target_files = [f.name for f in self.tables_path.glob("*.txt")]
        results = {}
        
        for filename in target_files:
            table_file = self.tables_path / filename
            if table_file.exists():
                results[filename] = self.check_table_file(table_file)
            else:
                print(f"  WARNING: Файл {filename} не найден")
                results[filename] = None
            print()
        
        return results
    
    def generate_report(self, results):
        """Генерирует отчет о состоянии таблиц"""
        print("=== ОТЧЕТ О СОСТОЯНИИ ТАБЛИЦ ===")
        
        total_reagents = 0
        total_problems = 0
        
        for filename, data in results.items():
            if data:
                total_reagents += data['total_reagents']
                total_problems += len(data['problems']) + data['empty_rows']
                
                status = "OK" if not data['problems'] and not data['empty_rows'] else "ПРОБЛЕМЫ"
                print(f"{filename}: {data['total_reagents']} реагентов - {status}")
        
        print(f"\nИТОГО:")
        print(f"- Всего реагентов в таблицах: {total_reagents}")
        print(f"- Всего проблем: {total_problems}")
        
        if total_problems == 0:
            print("Все таблицы в порядке!")
        else:
            print("Требуется дополнительная очистка")

def main():
    tables_path = "E:/GitRepo/MrCat/proverka/Таблицы"
    
    checker = TablesStatusChecker(tables_path)
    
    results = checker.check_all_tables()
    checker.generate_report(results)

if __name__ == "__main__":
    main()