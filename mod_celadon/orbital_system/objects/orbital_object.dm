/datum/orbital_object
	var/name = "неизвестно"
	//Unique ID of the orbital object
	var/unique_id = ""
	//Mass of the object in solar masses
	var/mass = 0
	//Radius of the object in arbitary space units
	var/radius = 1
	//What render mode to use
	var/render_mode = RENDER_MODE_DEFAULT
	//Position of the object (0,0) is the center of the map.
	var/datum/orbital_vector/position = new()
	//Velocity of the object
	var/datum/orbital_vector/velocity = new()
	//Static objects don't get moved.
	var/static_object = FALSE
	//Multiplier for velocity
	var/velocity_multiplier = 1
	//Do we ignore gravity?
	var/ignore_gravity = FALSE
	//Priority in the sorted list
	var/priority = 0

	//Delta time updates
	var/last_update_tick = 0

	//CALCULATED IN INIT
	//Once objects are outside of this range, we will not apply gravity to them.
	var/relevant_gravity_range
	//Are we currently immune to collisions
	var/collision_ignored = TRUE
	//What are we colliding with
	var/list/datum/orbital_object/colliding_with

	//The index or the orbital map we exist in
	var/orbital_map_index = PRIMARY_ORBITAL_MAP

	//Our collision type
	var/collision_type = COLLISION_UNDEFINED
	//The collision flags we register with
	var/collision_flags = NONE

	//The color of the locator
	var/locator_colour

/datum/orbital_object/New(datum/orbital_vector/position, datum/orbital_vector/velocity, orbital_map_index)
	if(orbital_map_index)
		src.orbital_map_index = orbital_map_index
	if(position)
		src.position = position
	else
		src.position = new /datum/orbital_vector(0, 0)
	if(velocity)
		src.velocity = velocity
	var/static/created_amount = 0
	unique_id = "[++created_amount]"
	. = ..()
	//Calculate relevant grav range
	relevant_gravity_range = sqrt((mass * GRAVITATIONAL_CONSTANT) / MINIMUM_EFFECTIVE_GRAVITATIONAL_ACCEELRATION)
	//Process this
	if(!static_object)
		START_PROCESSING(SSorbits, src)
	//Add to orbital map
	var/datum/orbital_map/map = SSorbits.orbital_maps[src.orbital_map_index]
	map.add_body(src)
	//If orbits has already setup, then post map setup
	if(SSorbits.orbits_setup)
		post_map_setup()
	var/validFirstColours = list("8", "9", "A", "B", "C", "D", "E", "F")
	locator_colour = "[pick(validFirstColours)][pick(GLOB.hex_characters)][pick(validFirstColours)][pick(GLOB.hex_characters)][pick(validFirstColours)][pick(GLOB.hex_characters)]"

/datum/orbital_object/Destroy()
	STOP_PROCESSING(SSorbits, src)
	var/datum/orbital_map/map = SSorbits.orbital_maps[orbital_map_index]
	map.remove_body(src)
	. = ..()

/datum/orbital_object/process(delta_time)
	//Dont process updates for static objects.
	if(static_object)
		return PROCESS_KILL

	last_update_tick = world.time

	var/datum/orbital_map/parent_map = SSorbits.orbital_maps[orbital_map_index]

	//===================================
	// GRAVITATIONAL ATTRACTION
	//===================================
	//Gravity is not considered while we have just undocked and are at the center of a massive body.
	if(!collision_ignored && !ignore_gravity)
		//Find relevant gravitational bodies.
		var/list/gravitational_bodies = parent_map.get_relevnant_bodies(src)
		//Calculate acceleration vector
		var/datum/orbital_vector/acceleration_per_second = new()
		//Calculate gravity
		for(var/datum/orbital_object/gravitational_body as() in gravitational_bodies)
			//https://en.wikipedia.org/wiki/Gravitational_acceleration
			var/distance = position.DistanceTo(gravitational_body.position)
			if(!distance)
				continue
			var/acceleration_amount = (GRAVITATIONAL_CONSTANT * gravitational_body.mass) / (distance * distance)
			//Calculate acceleration direction
			var/datum/orbital_vector/direction = new (gravitational_body.position.GetX() - position.GetX(), gravitational_body.position.GetY() - position.GetY())
			direction.NormalizeSelf()
			direction.ScaleSelf(acceleration_amount)
			//Add on the gravitational acceleration
			acceleration_per_second.AddSelf(direction)
		//Divide acceleration per second by the tick rate
		accelerate_towards(acceleration_per_second, delta_time)

	//===================================
	// MOVEMENT
	//===================================
	//Remember this
	var/prev_x = position.GetX()
	var/prev_y = position.GetY()

	//Move the gravitational body.
	var/datum/orbital_vector/vel_new = new(velocity.GetX() * delta_time * velocity_multiplier, velocity.GetY() * delta_time * velocity_multiplier)
	position.protected = FALSE
	position.AddSelf(vel_new)
	position.protected = TRUE

	//Oh we moved btw
	parent_map.on_body_move(src, prev_x, prev_y)

	//===================================
	// COLLISION CHECKING
	//===================================
	var/colliding = FALSE
	LAZYCLEARLIST(colliding_with)

	//Calculate our current position
	var/section_x = round(position.GetX() / ORBITAL_MAP_ZONE_SIZE)
	var/section_y = round(position.GetY() / ORBITAL_MAP_ZONE_SIZE)

	var/position_key = "[section_x],[section_y]"

	var/list/valid_objects = list()
	valid_objects += parent_map.get_all_bodies()

	//Only check nearby segments for collision objects
	if(parent_map.collision_zone_bodies[position_key])
		valid_objects += parent_map.collision_zone_bodies[position_key]

	for(var/datum/orbital_object/object as() in valid_objects)
		if(object == src)
			continue
		if(!(object.collision_type & collision_flags) && !(object.static_object && (collision_type & object.collision_flags)))
			continue
		var/distance = object.position.DistanceTo(position)
		if(distance < radius + object.radius)
			//Collision
			LAZYADD(colliding_with, object)
			collision(object)
			//Static objects dont check collisions, so call their collision proc for them.
			if(object.static_object)
				object.collision(src)
			colliding = TRUE
	if(!colliding)
		collision_ignored = FALSE

//We do a little suvatting
/datum/orbital_object/proc/accelerate_towards(datum/orbital_vector/acceleration_vector, time)
	velocity.AddSelf(acceleration_vector.ScaleSelf(time))

//Called when we collide with another orbital object.
/datum/orbital_object/proc/collision(datum/orbital_object/other)
	return

/datum/orbital_object/proc/post_map_setup()
	return

/datum/orbital_object/proc/get_locator_name()
	return name

/datum/orbital_object/proc/is_stealth()
	return FALSE