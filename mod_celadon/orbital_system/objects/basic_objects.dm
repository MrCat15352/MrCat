//Basic orbital objects for testing

/datum/orbital_object/planet
	name = "Планета"
	mass = 100
	radius = 20
	render_mode = RENDER_MODE_PLANET
	static_object = TRUE
	collision_type = COLLISION_Z_LINKED

/datum/orbital_object/beacon
	name = "Маяк"
	mass = 1
	radius = 5
	render_mode = RENDER_MODE_BEACON
	static_object = TRUE
	collision_type = COLLISION_Z_LINKED

/datum/orbital_object/shuttle
	name = "Шаттл"
	mass = 5
	radius = 3
	render_mode = RENDER_MODE_SHUTTLE
	collision_type = COLLISION_SHUTTLES
	collision_flags = COLLISION_Z_LINKED