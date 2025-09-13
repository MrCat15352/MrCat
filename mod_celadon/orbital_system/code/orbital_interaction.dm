//Orbital mode interaction system

/datum/overmap/ship/controlled/show_interaction_menu(mob/user, datum/overmap/target)
	. = ..()
	//Allow joining orbital mode if target is in orbital mode
	if(istype(target, /datum/overmap/ship/controlled))
		var/datum/overmap/ship/controlled/target_ship = target
		if(target_ship.in_orbital_mode && !in_orbital_mode && x == target_ship.saved_x && y == target_ship.saved_y)
			if(tgui_alert(user, "Корабль [target_ship.name] находится в орбитальном режиме. Присоединиться?", "Орбитальный режим", list("Да", "Нет")) == "Да")
				enter_orbital_mode()
				return "Присоединились к орбитальному бою."