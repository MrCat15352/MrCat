//Performance optimizations for orbital system

/datum/controller/subsystem/processing/orbits
	//Optimization flags
	var/max_objects_per_tick = 10
	var/skip_collision_checks = FALSE
	var/reduced_precision_mode = FALSE

/datum/controller/subsystem/processing/orbits/fire(resumed)
	if(resumed)
		. = ..()
		if(MC_TICK_CHECK)
			return
		//Update UIs with reduced frequency
		if(times_fired % 3 == 0)
			for(var/datum/tgui/tgui as() in open_orbital_maps)
				if(!tgui)
					continue
				tgui.send_update()
	
	//Limit processing objects per tick for performance
	var/processed_count = 0
	for(var/datum/orbital_object/obj in processing)
		if(processed_count >= max_objects_per_tick)
			break
		obj.process(wait * 0.1)
		processed_count++
		if(MC_TICK_CHECK)
			return
	
	if(!resumed)
		. = ..()
		if(MC_TICK_CHECK)
			return
		//Update UIs with reduced frequency
		if(times_fired % 3 == 0)
			for(var/datum/tgui/tgui as() in open_orbital_maps)
				if(!tgui)
					continue
				tgui.send_update()

//Optimized collision detection
/datum/orbital_object/process(delta_time)
	if(static_object)
		return PROCESS_KILL

	last_update_tick = world.time
	var/datum/orbital_map/parent_map = SSorbits.orbital_maps[orbital_map_index]

	//Skip expensive calculations if in reduced precision mode
	if(!SSorbits.reduced_precision_mode && !collision_ignored && !ignore_gravity)
		//Simplified gravity calculation
		var/list/gravitational_bodies = parent_map.get_relevnant_bodies(src)
		if(length(gravitational_bodies) > 0)
			var/datum/orbital_vector/acceleration_per_second = new()
			for(var/datum/orbital_object/gravitational_body as() in gravitational_bodies)
				var/distance = position.DistanceTo(gravitational_body.position)
				if(!distance || distance > gravitational_body.relevant_gravity_range)
					continue
				var/acceleration_amount = (GRAVITATIONAL_CONSTANT * gravitational_body.mass) / (distance * distance)
				var/datum/orbital_vector/direction = new(gravitational_body.position.GetX() - position.GetX(), gravitational_body.position.GetY() - position.GetY())
				direction.NormalizeSelf()
				direction.ScaleSelf(acceleration_amount)
				acceleration_per_second.AddSelf(direction)
			accelerate_towards(acceleration_per_second, delta_time)

	//Movement
	var/prev_x = position.GetX()
	var/prev_y = position.GetY()
	var/datum/orbital_vector/vel_new = new(velocity.GetX() * delta_time * velocity_multiplier, velocity.GetY() * delta_time * velocity_multiplier)
	position.protected = FALSE
	position.AddSelf(vel_new)
	position.protected = TRUE
	parent_map.on_body_move(src, prev_x, prev_y)

	//Skip collision detection if disabled for performance
	if(!SSorbits.skip_collision_checks)
		check_collisions(parent_map)

/datum/orbital_object/proc/check_collisions(datum/orbital_map/parent_map)
	var/colliding = FALSE
	LAZYCLEARLIST(colliding_with)
	
	var/section_x = round(position.GetX() / ORBITAL_MAP_ZONE_SIZE)
	var/section_y = round(position.GetY() / ORBITAL_MAP_ZONE_SIZE)
	var/position_key = "[section_x],[section_y]"
	
	var/list/valid_objects = list()
	if(parent_map.collision_zone_bodies[position_key])
		valid_objects += parent_map.collision_zone_bodies[position_key]
	
	for(var/datum/orbital_object/object as() in valid_objects)
		if(object == src)
			continue
		if(!(object.collision_type & collision_flags) && !(object.static_object && (collision_type & object.collision_flags)))
			continue
		var/distance = object.position.DistanceTo(position)
		if(distance < radius + object.radius)
			LAZYADD(colliding_with, object)
			collision(object)
			if(object.static_object)
				object.collision(src)
			colliding = TRUE
	
	if(!colliding)
		collision_ignored = FALSE