PROCESSING_SUBSYSTEM_DEF(orbits)
	name = "Орбиты"
	flags = SS_KEEP_TIMING
	init_order = INIT_ORDER_ORBITS
	priority = FIRE_PRIORITY_ORBITS
	wait = ORBITAL_UPDATE_RATE

	//The primary orbital map.
	var/list/orbital_maps = list()

	var/datum/orbital_map_tgui/orbital_map_tgui = new()

	var/orbits_setup = FALSE

	var/list/datum/orbital_objective/possible_objectives = list()
	var/datum/orbital_objective/current_objective

	//key = port_id, value = orbital shuttle object
	var/list/assoc_shuttles = list()

	//key = z-level as string, value = orbital object for that z-level
	var/list/assoc_z_levels = list()

	//Key = port_id, value = world time of next launch
	var/list/interdicted_shuttles = list()

	var/next_objective_time = 0

	var/list/datum/tgui/open_orbital_maps = list()

	//The station
	var/datum/orbital_object/station_instance

	//Assoc shuttle data
	//Key: port_id, Value: The shuttle data
	var/list/assoc_shuttle_data = list()

/datum/controller/subsystem/processing/orbits/Initialize(start_timeofday)
	//Create the main orbital map.
	orbital_maps[PRIMARY_ORBITAL_MAP] = new /datum/orbital_map()
	//Setup orbits immediately
	post_load_init()
	return ..()

/datum/controller/subsystem/processing/orbits/proc/post_load_init()
	for(var/map_key in orbital_maps)
		var/datum/orbital_map/orbital_map = orbital_maps[map_key]
		orbital_map.post_setup()
	orbits_setup = TRUE
	//Create test objects
	new /datum/orbital_object/planet(new /datum/orbital_vector(0, 0))
	new /datum/orbital_object/station(new /datum/orbital_vector(-30, -30))
	new /datum/orbital_object/beacon(new /datum/orbital_vector(50, 0))
	new /datum/orbital_object/shuttle(new /datum/orbital_vector(30, 30), new /datum/orbital_vector(0, 1))

/datum/controller/subsystem/processing/orbits/fire(resumed)
	if(resumed)
		. = ..()
		if(MC_TICK_CHECK)
			return
		//Update UIs
		for(var/datum/tgui/tgui as() in open_orbital_maps)
			if(!tgui)
				continue
			tgui.send_update()
	//Do processing.
	if(!resumed)
		. = ..()
		if(MC_TICK_CHECK)
			return
		//Update UIs
		for(var/datum/tgui/tgui as() in open_orbital_maps)
			if(!tgui)
				continue
			tgui.send_update()

/datum/controller/subsystem/processing/orbits/proc/get_orbital_map_base_data(
		datum/orbital_map/showing_map,
		user_ref,
		see_stealthed = FALSE,
		datum/orbital_object/attached_orbital_object = null,
		datum/shuttle_data/attached_data = null
	)
	var/data = list()
	data["update_index"] = SSorbits.times_fired
	data["map_objects"] = list()
	//Get the objects
	for(var/datum/orbital_object/object as() in showing_map.get_all_bodies())
		if(!object)
			continue
		//we can't see it, unless we are stealth too
		if(!see_stealthed && object.is_stealth())
			continue
		//Transmit map data about non single-instanced objects.
		data["map_objects"] += list(list(
			"id" = object.unique_id,
			"name" = object.name,
			"position_x" = object.position.GetX(),
			"position_y" = object.position.GetY(),
			"velocity_x" = object.velocity.GetX(),
			"velocity_y" = object.velocity.GetY(),
			"radius" = object.radius,
			"render_mode" = object.render_mode,
			"priority" = object.priority,
			"vel_mult" = object.velocity_multiplier,
		))
	return data

/datum/controller/subsystem/processing/orbits/proc/get_shuttle_data(port_id)
	RETURN_TYPE(/datum/shuttle_data)
	return assoc_shuttle_data[port_id]

/datum/controller/subsystem/processing/orbits/proc/register_shuttle(port_id)
	var/datum/shuttle_data/new_shuttle = new(port_id)
	assoc_shuttle_data[port_id] = new_shuttle

/datum/controller/subsystem/processing/orbits/proc/remove_shuttle(port_id)
	var/datum/shuttle_data/shuttle = get_shuttle_data(port_id)
	assoc_shuttle_data -= port_id
	qdel(shuttle)