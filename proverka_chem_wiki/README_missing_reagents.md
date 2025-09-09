# Инструменты для работы с отсутствующими реагентами

Этот набор скриптов предназначен для обработки отсутствующих реагентов в таблицах химических веществ.

## Доступные скрипты

### 1. `remove_missing_reagents.py`
Простой скрипт для удаления отсутствующих реагентов из таблиц.

**Использование:**
```bash
python remove_missing_reagents.py
```

**Что делает:**
- Удаляет строки таблиц с отсутствующими реагентами
- Обрабатывает файлы: Лекарства.txt, Наркотики.txt, Пиротехника.txt

### 2. `replace_missing_reagents.py`
Скрипт для замены отсутствующих реагентов альтернативными.

**Использование:**
```bash
python replace_missing_reagents.py
```

**Что делает:**
- Заменяет отсутствующие реагенты на альтернативные
- Обновляет anchor и названия реагентов

### 3. `fix_missing_reagents.py` (Рекомендуется)
Универсальный скрипт с возможностью выбора действия.

**Использование:**
```bash
# Удаление отсутствующих реагентов (по умолчанию)
python fix_missing_reagents.py

# Замена отсутствующих реагентов
python fix_missing_reagents.py --action replace

# Указание пути к таблицам
python fix_missing_reagents.py --tables-path "путь/к/таблицам"
```

**Параметры:**
- `--action`: `remove` (удалить) или `replace` (заменить)
- `--tables-path`: путь к папке с таблицами

### 4. `check_tables_status.py`
Скрипт для проверки состояния таблиц после обработки.

**Использование:**
```bash
python check_tables_status.py
```

**Что показывает:**
- Количество реагентов в каждой таблице
- Найденные проблемы (отсутствующие реагенты, поврежденные anchor)
- Общую статистику

## Отсутствующие реагенты

### Лекарства.txt
- Seiver
- Skeleton's Boon
- Pucetylline Essence
- Chartreuse Solution
- Restorative Nanites
- Medicated Suture

### Наркотики.txt
- Krokodil
- Bath Salts

### Пиротехника.txt
- Fluorosurfactant
- Smoke
- Explosion
- EMP
- Teslium Shock

## Рекомендуемые замены

### Лекарства.txt
- Skeleton's Boon → Calcium
- Pucetylline Essence → Charcoal
- Chartreuse Solution → Pentetic Acid
- Restorative Nanites → Omnizine
- Medicated Suture → Synthflesh

### Наркотики.txt
- Bath Salts → Methamphetamine

### Пиротехника.txt
- Teslium Shock → Teslium

## Результаты работы

После запуска `remove_missing_reagents.py`:
- Удалено 3 записи с отсутствующими реагентами
- Очищены таблицы от неработающих ссылок

Текущее состояние таблиц:
- Лекарства.txt: 17 реагентов
- Наркотики.txt: 3 реагента  
- Пиротехника.txt: 1 реагент
- Токсины.txt: 100 реагентов
- **Всего:** 121 реагент

## Рекомендации

1. **Для очистки:** Используйте `fix_missing_reagents.py` с параметром `--action remove`
2. **Для замены:** Используйте `fix_missing_reagents.py` с параметром `--action replace`
3. **Для проверки:** Запустите `check_tables_status.py` после обработки
4. **Резервное копирование:** Создайте копии таблиц перед обработкой

## Примеры использования

```bash
# Создать резервную копию
cp -r "Таблицы" "Таблицы_backup"

# Удалить отсутствующие реагенты
python fix_missing_reagents.py --action remove

# Проверить результат
python check_tables_status.py

# При необходимости заменить на альтернативные
python fix_missing_reagents.py --action replace
```