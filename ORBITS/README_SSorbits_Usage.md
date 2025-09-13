# Файлы, использующие подсистему SSorbits

## Основные системные файлы

### Контроллеры подсистем
- `code/controllers/subsystem/mapping.dm`
- `code/controllers/subsystem/processing/orbits.dm` - основная подсистема орбит
- `code/controllers/subsystem/rust.dm`
- `code/controllers/subsystem/ticker.dm`
- `code/controllers/subsystem/violence.dm`
- `code/controllers/subsystem/zclear.dm`

### Игровые модули
- `code/game/turfs/open/space/transit.dm`
- `code/modules/admin/verbs/shuttlepanel.dm`
- `code/modules/events/meteor_wave.dm`
- `code/modules/mapping/space_management/space_level.dm`
- `code/modules/projectiles/projectile/shuttle.dm`
- `code/modules/shuttle/bluespace_shuttle_pod/pod_computer.dm`
- `code/modules/shuttle/shuttle.dm`

### Определения и хелперы
- `code/__DEFINES/dcs/signals.dm`
- `code/__DEFINES/orbit_defines.dm`
- `code/__HELPERS/names.dm`

## Орбитальная система (white/valtos)

### Интерфейсы
- `white/valtos/code/exploration/super_cruise/interface/orbital_map_interface.dm`

### Компоненты орбитальной карты
- `white/valtos/code/exploration/super_cruise/orbital_map_components/orbital_map_helpers.dm`
- `white/valtos/code/exploration/super_cruise/orbital_map_components/orbital_object.dm`

### Орбитальные объекты
- `white/valtos/code/exploration/super_cruise/orbital_map_components/orbital_objects/beacon.dm`
- `white/valtos/code/exploration/super_cruise/orbital_map_components/orbital_objects/lavaland.dm`
- `white/valtos/code/exploration/super_cruise/orbital_map_components/orbital_objects/phobos.dm`
- `white/valtos/code/exploration/super_cruise/orbital_map_components/orbital_objects/space_station.dm`
- `white/valtos/code/exploration/super_cruise/orbital_map_components/orbital_objects/shuttle/shuttle.dm`

### Генератор POI и заданий
- `white/valtos/code/exploration/super_cruise/orbital_poi_generator/loot/research_disks.dm`
- `white/valtos/code/exploration/super_cruise/orbital_poi_generator/objective_computer.dm`
- `white/valtos/code/exploration/super_cruise/orbital_poi_generator/ruin_generator/ruin_generator.dm`
- `white/valtos/code/exploration/super_cruise/orbital_poi_generator/_orbital_objective.dm`

### Система шаттлов
- `white/valtos/code/exploration/super_cruise/shuttle_ai_pilot/shuttle_autopilot.dm`
- `white/valtos/code/exploration/super_cruise/shuttle_components/portable_orbital_map.dm`
- `white/valtos/code/exploration/super_cruise/shuttle_components/shuttle_console.dm`
- `white/valtos/code/exploration/super_cruise/shuttle_components/thrust/shuttle_engine.dm`
- `white/valtos/code/exploration/super_cruise/shuttle_data/shuttle_data.dm`
- `white/valtos/code/exploration/super_cruise/shuttle_supercruise.dm`

### Система оружия
- `white/valtos/code/exploration/super_cruise/weapons/shuttle_weapon.dm`
- `white/valtos/code/exploration/super_cruise/weapons/weapon_controller.dm`

### Отладка и утилиты
- `white/valtos/code/exploration/super_cruise/debug_verbs.dm`
- `white/valtos/code/exploration/research_locator.dm`

## Дополнительные модули

### Создание шаттлов
- `white/valtos/code/shuttle_creation/_shuttle_creator.dm`

### Специальные шаттлы
- `white/valtos/code/yohei/shuttle.dm`

### Орбитальные утилиты (baldenysh)
- `white/baldenysh/govnokod/orbital_stuff/procs.dm`

## Основные функции SSorbits

### Управление орбитальными картами
- `orbital_maps` - все орбитальные карты
- `open_orbital_maps` - открытые UI карт
- `get_orbital_map_base_data()` - получение данных карты

### Управление шаттлами
- `assoc_shuttles` - ассоциация шаттлов с орбитальными объектами
- `assoc_shuttle_data` - данные шаттлов
- `get_shuttle_data()` - получение данных шаттла
- `register_shuttle()` / `remove_shuttle()` - регистрация шаттлов
- `interdicted_shuttles` - перехваченные шаттлы

### Управление Z-уровнями
- `assoc_z_levels` - связь Z-уровней с орбитальными объектами
- `ruin_levels` - счетчик уровней руин

### Система заданий
- `possible_objectives` - возможные задания
- `current_objective` - текущее задание
- `next_objective_time` - время следующего задания
- `assign_objective()` - назначение задания

### Система событий
- `ruin_events` - события руин
- `runnable_events` - запускаемые события
- `get_event()` - получение события

### Исследования и лут
- `research_disks` - исследовательские диски
- `shuttle_weapons` - оружие шаттлов

### Станция
- `station_instance` - экземпляр главной станции

### Обработка
- `processing` - обрабатываемые объекты
- `times_fired` - счетчик обновлений
- `orbits_setup` - флаг настройки орбит