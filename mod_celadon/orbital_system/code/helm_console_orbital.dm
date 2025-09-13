//Helm console orbital mode integration

/obj/machinery/computer/helm
	var/orbital_mode = FALSE

/obj/machinery/computer/helm/ui_data(mob/user)
	var/list/data = ..()
	
	var/datum/overmap/ship/controlled/ship = SSovermap.get_overmap_object_by_location(src)
	if(istype(ship))
		data["orbital_mode"] = ship.in_orbital_mode
		data["can_enter_orbital"] = !ship.in_orbital_mode
		data["can_exit_orbital"] = ship.in_orbital_mode
		
		if(ship.in_orbital_mode && ship.current_local_map)
			data["local_map_data"] = ship.current_local_map.get_ui_data()
	
	return data

/obj/machinery/computer/helm/ui_act(action, list/params, datum/tgui/ui, datum/ui_state/state)
	. = ..()
	if(.)
		return
	
	var/datum/overmap/ship/controlled/ship = SSovermap.get_overmap_object_by_location(src)
	if(!istype(ship))
		return
	
	switch(action)
		if("enter_orbital_mode")
			if(ship.enter_orbital_mode())
				. = TRUE
		if("exit_orbital_mode")
			if(ship.exit_orbital_mode())
				. = TRUE
		if("orbital_move")
			if(ship.in_orbital_mode)
				var/dir = text2num(params["direction"])
				ship.orbital_move(dir)
				. = TRUE

//Ship orbital movement in local map
/datum/overmap/ship/controlled
	var/local_x = 0
	var/local_y = 0
	var/local_vel_x = 0
	var/local_vel_y = 0

/datum/overmap/ship/controlled/proc/orbital_move(direction)
	if(!in_orbital_mode || !current_local_map)
		return
	
	var/thrust = 5
	switch(direction)
		if(NORTH)
			local_vel_y += thrust
		if(SOUTH)
			local_vel_y -= thrust
		if(EAST)
			local_vel_x += thrust
		if(WEST)
			local_vel_x -= thrust
	
	//Apply movement
	local_x += local_vel_x
	local_y += local_vel_y
	
	//Bounds checking
	local_x = clamp(local_x, 0, current_local_map.map_size)
	local_y = clamp(local_y, 0, current_local_map.map_size)
	
	//Apply drag
	local_vel_x *= 0.95
	local_vel_y *= 0.95

/datum/local_orbital_map/proc/get_ui_data()
	var/list/data = list()
	data["map_size"] = map_size
	data["ships"] = list()
	data["obstacles"] = obstacles
	
	for(var/datum/overmap/ship/controlled/ship in ships)
		data["ships"] += list(list(
			"name" = ship.name,
			"x" = ship.local_x,
			"y" = ship.local_y,
			"vel_x" = ship.local_vel_x,
			"vel_y" = ship.local_vel_y
		))
	
	return data