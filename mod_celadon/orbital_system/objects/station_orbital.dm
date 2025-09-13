//Station as orbital object

/datum/orbital_object/station
	name = "Космическая станция"
	mass = 1000
	radius = 50
	render_mode = RENDER_MODE_BEACON
	static_object = TRUE
	collision_type = COLLISION_Z_LINKED
	priority = 100

/datum/orbital_object/station/post_map_setup()
	// Link to main station if exists
	if(GLOB.station_name)
		name = GLOB.station_name