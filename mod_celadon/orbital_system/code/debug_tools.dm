//Debug tools for orbital system

/client/verb/orbital_debug_panel()
	set name = "Orbital Debug Panel"
	set category = "Debug"
	
	#ifdef ORBITAL_SYSTEM_ENABLED
	var/dat = {"
	<html><head><title>Orbital System Debug</title></head><body>
	<h2>Orbital System Status</h2>
	<p><b>Initialized:</b> [SSorbits.initialized ? "Yes" : "No"]</p>
	<p><b>Orbits Setup:</b> [SSorbits.orbits_setup ? "Yes" : "No"]</p>
	<p><b>Processing Objects:</b> [length(SSorbits.processing)]</p>
	<p><b>Open UIs:</b> [length(SSorbits.open_orbital_maps)]</p>
	<p><b>Times Fired:</b> [SSorbits.times_fired]</p>
	
	<h3>Orbital Maps</h3>
	"}
	
	for(var/map_key in SSorbits.orbital_maps)
		var/datum/orbital_map/map = SSorbits.orbital_maps[map_key]
		dat += "<p><b>[map_key]:</b> [length(map.get_all_bodies())] objects</p>"
	
	dat += {"
	<h3>Actions</h3>
	<a href='byond://?src=[REF(src)];orbital_debug=refresh'>Refresh</a> |
	<a href='byond://?src=[REF(src)];orbital_debug=create_test'>Create Test Object</a> |
	<a href='byond://?src=[REF(src)];orbital_debug=clear_objects'>Clear All Objects</a> |
	<a href='byond://?src=[REF(src)];orbital_debug=performance'>Toggle Performance Mode</a>
	</body></html>
	"}
	
	usr << browse(dat, "window=orbital_debug;size=500x400")
	#else
	to_chat(src, "Orbital system not compiled.")
	#endif

/client/Topic(href, href_list)
	. = ..()
	if(href_list["orbital_debug"])
		
		#ifdef ORBITAL_SYSTEM_ENABLED
		switch(href_list["orbital_debug"])
			if("refresh")
				orbital_debug_panel()
			if("create_test")
				new /datum/orbital_object/shuttle(new /datum/orbital_vector(rand(-100, 100), rand(-100, 100)), new /datum/orbital_vector(rand(-5, 5), rand(-5, 5)))
				to_chat(src, "Created test orbital object")
				orbital_debug_panel()
			if("clear_objects")
				var/count = 0
				for(var/datum/orbital_object/obj in SSorbits.processing)
					qdel(obj)
					count++
				to_chat(src, "Deleted [count] orbital objects")
				orbital_debug_panel()
			if("performance")
				SSorbits.reduced_precision_mode = !SSorbits.reduced_precision_mode
				to_chat(src, "Performance mode: [SSorbits.reduced_precision_mode ? "ON" : "OFF"]")
				orbital_debug_panel()
		#endif

/client/verb/create_orbital_object()
	set name = "Create Orbital Object"
	set category = "Debug"
	
	#ifdef ORBITAL_SYSTEM_ENABLED
	var/list/types = list(
		"Planet" = /datum/orbital_object/planet,
		"Station" = /datum/orbital_object/station,
		"Beacon" = /datum/orbital_object/beacon,
		"Shuttle" = /datum/orbital_object/shuttle
	)
	
	var/choice = input("Select object type:", "Create Orbital Object") as null|anything in types
	if(!choice)
		return
	
	var/x_pos = input("X Position:", "Position", 0) as num
	var/y_pos = input("Y Position:", "Position", 0) as num
	var/x_vel = input("X Velocity:", "Velocity", 0) as num
	var/y_vel = input("Y Velocity:", "Velocity", 0) as num
	
	var/obj_type = types[choice]
	new obj_type(new /datum/orbital_vector(x_pos, y_pos), new /datum/orbital_vector(x_vel, y_vel))
	
	to_chat(src, "Created [choice] at ([x_pos], [y_pos]) with velocity ([x_vel], [y_vel])")
	#else
	to_chat(src, "Orbital system not compiled.")
	#endif

//Performance monitoring
/datum/controller/subsystem/processing/orbits
	var/performance_stats = list()
	var/last_performance_check = 0

/datum/controller/subsystem/processing/orbits/fire(resumed)
	var/start_time = world.timeofday
	. = ..()
	var/end_time = world.timeofday
	
	//Track performance every 30 seconds
	if(world.time > last_performance_check + 30 SECONDS)
		var/processing_time = end_time - start_time
		performance_stats["processing_time"] = processing_time
		performance_stats["object_count"] = length(processing)
		performance_stats["ui_count"] = length(open_orbital_maps)
		performance_stats["last_update"] = world.time
		last_performance_check = world.time
		
		//Auto-enable performance mode if needed
		if(processing_time > 50 && !reduced_precision_mode)
			log_world("ORBITAL SYSTEM: Auto-enabling performance mode due to high processing time ([processing_time]ms)")
			reduced_precision_mode = TRUE
			max_objects_per_tick = 5