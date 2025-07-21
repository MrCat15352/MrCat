// Пример использования специального лифта для телепортации на centcom_ship.dmm

// Для использования в карте:
// 1. Разместите обычную платформу лифта /obj/structure/elevator_platform
// 2. Разместите лендмарк /obj/effect/landmark/outpost/elevator/special/centcom на той же клетке
// 3. Настройте координаты назначения в лендмарке (target_x, target_y, target_z)
// 4. Добавьте кнопки и другие элементы лифта как обычно

/*
Пример размещения в .dmm файле:

"a" = (
/obj/structure/elevator_platform,
/obj/effect/landmark/outpost/elevator/special/centcom{
    target_x = 128;
    target_y = 128;
    target_z = 1
    },
/turf/open/floor/plasteel,
/area/template_noop
)

"b" = (
/obj/structure/elevator_platform,
/obj/machinery/elevator_floor_button{
    pixel_y = 25
    },
/turf/open/floor/plasteel,
/area/template_noop
)

"c" = (
/obj/structure/elevator_platform,
/obj/machinery/status_display/elevator{
    pixel_y = 32
    },
/turf/open/floor/plasteel,
/area/template_noop
)
*/