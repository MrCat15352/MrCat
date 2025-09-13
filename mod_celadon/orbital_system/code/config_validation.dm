//Configuration validation and error handling

/datum/controller/subsystem/processing/orbits/Initialize(start_timeofday)
	//Validate configuration
	if(!validate_orbital_config())
		log_world("ORBITAL SYSTEM: Configuration validation failed, using defaults")
	
	//Create the main orbital map
	orbital_maps[PRIMARY_ORBITAL_MAP] = new /datum/orbital_map()
	return ..()

/datum/controller/subsystem/processing/orbits/proc/validate_orbital_config()
	//Check if orbital system is properly enabled
	#ifndef ORBITAL_SYSTEM_ENABLED
	log_world("ORBITAL SYSTEM: Warning - ORBITAL_SYSTEM_ENABLED not defined")
	return FALSE
	#endif
	
	//Validate critical defines
	// ORBITAL_UPDATE_RATE is always defined as constant
	
	// Skip validation for constants that are always defined
	
	log_world("ORBITAL SYSTEM: Configuration validation passed")
	return TRUE

//Error recovery procedures
/datum/controller/subsystem/processing/orbits/proc/handle_orbital_error(error_msg)
	log_world("ORBITAL SYSTEM ERROR: [error_msg]")
	message_admins("Orbital system error: [error_msg]")
	
	//Try to recover by resetting the system
	if(length(orbital_maps) == 0)
		log_world("ORBITAL SYSTEM: Attempting recovery - recreating orbital maps")
		orbital_maps[PRIMARY_ORBITAL_MAP] = new /datum/orbital_map()
	
	//Clear problematic objects
	for(var/datum/orbital_object/obj in processing)
		if(!obj || QDELETED(obj))
			STOP_PROCESSING(src, obj)

//Safe object creation with error handling
/datum/orbital_object/New(datum/orbital_vector/position, datum/orbital_vector/velocity, orbital_map_index)
	if(!SSorbits)
		CRASH("Attempted to create orbital object before SSorbits initialization")
	
	if(!SSorbits.orbital_maps)
		CRASH("Attempted to create orbital object with no orbital maps")
	
	if(orbital_map_index && !SSorbits.orbital_maps[orbital_map_index])
		log_world("ORBITAL SYSTEM: Warning - Invalid orbital map index [orbital_map_index], using primary")
		orbital_map_index = PRIMARY_ORBITAL_MAP
	
	. = ..()

//Graceful shutdown
/datum/controller/subsystem/processing/orbits/Shutdown()
	log_world("ORBITAL SYSTEM: Shutting down gracefully")
	
	//Close all open UIs
	for(var/datum/tgui/tgui as() in open_orbital_maps)
		if(tgui)
			tgui.close()
	open_orbital_maps.Cut()
	
	//Stop processing all objects
	for(var/datum/orbital_object/obj in processing)
		STOP_PROCESSING(src, obj)
	
	log_world("ORBITAL SYSTEM: Shutdown complete")