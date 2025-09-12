# Установка системы Bounty Hunter

## Созданные файлы

### Основная логика:
- `code/datums/bounty_hunter.dm` - Датум для bounty заявок и глобальные функции
- `code/game/machinery/computer/bounty_hunter_console.dm` - Консоль bounty hunter
- `code/game/objects/items/circuitboards/computer_circuitboards_bounty.dm` - Плата консоли

### UI интерфейс:
- `tgui/packages/tgui/interfaces/BountyHunter.tsx` - TGUI интерфейс

### Карго и тестирование:
- `code/modules/cargo/packs/bounty_hunter.dm` - Карго пакет для покупки консоли
- `code/modules/unit_tests/bounty_hunter_test.dm` - Unit тест системы

### Документация:
- `BOUNTY_HUNTER_README.md` - Подробное описание системы
- `BOUNTY_HUNTER_INSTALL.md` - Этот файл с инструкциями

## Изменения в существующих файлах

### shiptest.dme:
Добавлены следующие строки в соответствующие секции:
```dm
#include "code\datums\bounty_hunter.dm"
#include "code\game\machinery\computer\bounty_hunter_console.dm"
#include "code\game\objects\items\circuitboards\computer_circuitboards_bounty.dm"
#include "code\modules\cargo\packs\bounty_hunter.dm"
```

### code/modules/unit_tests/_unit_tests.dm:
Добавлена строка:
```dm
#include "bounty_hunter_test.dm"
```

## Проверка установки

1. **Компиляция**: Убедитесь, что проект компилируется без ошибок
2. **Тестирование**: Запустите unit тесты для проверки базового функционала
3. **В игре**: 
   - Закажите консоль через карго (Security Supplies -> Bounty Hunter Console Crate)
   - Постройте консоль из платы
   - Протестируйте создание и просмотр bounty заявок

## Использование

### Для администраторов:
- Консоль можно спавнить командой: `/obj/machinery/computer/bounty_hunter`
- Плату можно спавнить командой: `/obj/item/circuitboard/computer/bounty_hunter`

### Для игроков:
1. Закажите консоль через карго за 1500 кредитов
2. Постройте консоль из полученной платы
3. Используйте ID карту для авторизации
4. Создавайте и просматривайте bounty заявки

## Возможные проблемы

### Ошибки компиляции:
- Убедитесь, что все файлы добавлены в shiptest.dme
- Проверьте синтаксис в созданных файлах

### Проблемы с UI:
- Убедитесь, что TGUI файл находится в правильной директории
- Перекомпилируйте TGUI если необходимо

### Проблемы с деньгами:
- Система использует корабельные счета через ship_access
- Убедитесь, что у игрока есть доступ к кораблю с активным банковским счётом

## Дальнейшее развитие

Система готова к использованию в базовом виде. Возможные улучшения:
- Автоматическая выплата при выполнении bounty
- Система репутации
- Фракционные ограничения
- Интеграция с системами безопасности
- Уведомления о новых заявках