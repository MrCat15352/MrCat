//Local orbital map TGUI interface

/datum/local_orbital_tgui
	var/datum/overmap/ship/controlled/host_ship

/datum/local_orbital_tgui/New(datum/overmap/ship/controlled/ship)
	host_ship = ship

/datum/local_orbital_tgui/ui_interact(mob/user, datum/tgui/ui)
	to_chat(user, "Attempting to open LocalOrbitalMap interface...")
	ui = SStgui.try_update_ui(user, src, ui)
	if(!ui)
		to_chat(user, "Creating new UI...")
		ui = new(user, src, "LocalOrbitalMap", "Локальная орбитальная карта")
		ui.open()
		to_chat(user, "UI opened successfully")
	else
		to_chat(user, "UI updated")

/datum/local_orbital_tgui/ui_data(mob/user)
	if(!host_ship || !host_ship.current_local_map)
		return list()
	
	var/list/data = host_ship.current_local_map.get_ui_data()
	data["player_ship"] = host_ship.name
	return data

/datum/local_orbital_tgui/ui_act(action, list/params, datum/tgui/ui, datum/ui_state/state)
	if(!host_ship)
		return FALSE
	
	to_chat(usr, "Local orbital action: [action]")
	
	switch(action)
		if("orbital_move")
			var/direction = text2num(params["direction"])
			host_ship.orbital_move(direction)
			return TRUE
		if("exit_orbital_mode")
			host_ship.exit_orbital_mode()
			ui.close()
			return TRUE
	
	return FALSE

//Add to helm console
/obj/machinery/computer/helm/ui_act(action, list/params, datum/tgui/ui, datum/ui_state/state)
	. = ..()
	if(.)
		return
	
	var/datum/overmap/ship/controlled/ship = SSovermap.get_overmap_object_by_location(src)
	if(!istype(ship))
		return
	
	switch(action)
		if("open_local_orbital")
			if(ship.in_orbital_mode && ship.current_local_map)
				var/datum/local_orbital_tgui/interface = new(ship)
				interface.ui_interact(usr)
				. = TRUE