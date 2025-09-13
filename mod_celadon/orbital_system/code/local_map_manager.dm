//Local orbital map manager

/datum/controller/subsystem/processing/orbits
	var/list/local_orbital_maps = list()

/datum/controller/subsystem/processing/orbits/proc/get_local_map(sector_key, datum/overmap/ship/controlled/requesting_ship)
	//Check if map already exists
	if(local_orbital_maps[sector_key])
		return local_orbital_maps[sector_key]
	
	//Create new local map
	var/list/coords = splittext(sector_key, ",")
	var/x = text2num(coords[1])
	var/y = text2num(coords[2])
	
	var/datum/local_orbital_map/new_map = new(x, y)
	local_orbital_maps[sector_key] = new_map
	
	return new_map

/datum/controller/subsystem/processing/orbits/proc/cleanup_empty_maps()
	for(var/sector_key in local_orbital_maps)
		var/datum/local_orbital_map/map = local_orbital_maps[sector_key]
		if(!length(map.ships))
			//No ships in this sector, clean up after delay
			addtimer(CALLBACK(src, PROC_REF(remove_empty_map), sector_key), 5 MINUTES)

/datum/controller/subsystem/processing/orbits/proc/remove_empty_map(sector_key)
	var/datum/local_orbital_map/map = local_orbital_maps[sector_key]
	if(map && !length(map.ships))
		local_orbital_maps -= sector_key
		qdel(map)

//Process local orbital maps
/datum/controller/subsystem/processing/orbits/fire(resumed)
	. = ..()
	
	//Process local orbital combat
	for(var/sector_key in local_orbital_maps)
		var/datum/local_orbital_map/map = local_orbital_maps[sector_key]
		map.process()

/datum/local_orbital_map/proc/process()
	//Update ship positions
	for(var/datum/overmap/ship/controlled/ship in ships)
		//Apply physics, collision detection, etc
		ship.local_x += ship.local_vel_x * 0.1
		ship.local_y += ship.local_vel_y * 0.1
		
		//Bounds checking
		ship.local_x = clamp(ship.local_x, 0, map_size)
		ship.local_y = clamp(ship.local_y, 0, map_size)
		
		//Check collisions with obstacles
		check_ship_collisions(ship)