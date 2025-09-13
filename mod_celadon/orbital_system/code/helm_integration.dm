//Integration with existing helm console

/obj/machinery/computer/helm/proc/get_orbital_data()
	var/datum/overmap/ship/controlled/ship = SSovermap.get_overmap_object_by_location(src)
	if(!istype(ship))
		return list()
	
	return list(
		"orbital_mode" = ship.in_orbital_mode,
		"can_enter_orbital" = !ship.in_orbital_mode,
		"can_exit_orbital" = ship.in_orbital_mode,
		"has_local_map" = ship.in_orbital_mode && ship.current_local_map
	)

/obj/machinery/computer/helm/proc/handle_orbital_action(action, list/params, mob/user)
	var/datum/overmap/ship/controlled/ship = SSovermap.get_overmap_object_by_location(src)
	if(!istype(ship))
		return FALSE
	
	switch(action)
		if("enter_orbital_mode")
			return ship.enter_orbital_mode()
		if("exit_orbital_mode")
			return ship.exit_orbital_mode()
		if("open_local_orbital")
			if(ship.in_orbital_mode && ship.current_local_map)
				var/datum/local_orbital_tgui/interface = new(ship)
				interface.ui_interact(user)
				return TRUE
	
	return FALSE