//Local orbital combat mode

/datum/overmap/ship/controlled
	var/in_orbital_mode = FALSE
	var/datum/local_orbital_map/current_local_map

/datum/overmap/ship/controlled/proc/enter_orbital_mode()
	if(in_orbital_mode)
		return FALSE
	
	in_orbital_mode = TRUE
	//Find or create local orbital map for this sector
	var/sector_key = "[x],[y]"
	current_local_map = SSorbits.get_local_map(sector_key, src)
	
	//Freeze overmap movement
	velocity_x = 0
	velocity_y = 0
	
	//Add ship to local orbital map
	current_local_map.add_ship(src)
	
	//Notify crew
	priority_announce("Корабль вошел в режим орбитальной навигации.", "Навигация")
	return TRUE

/datum/overmap/ship/controlled/proc/exit_orbital_mode()
	if(!in_orbital_mode)
		return FALSE
	
	in_orbital_mode = FALSE
	
	//Remove from local map
	if(current_local_map)
		current_local_map.remove_ship(src)
		current_local_map = null
	
	//Notify crew
	priority_announce("Корабль вышел из режима орбитальной навигации.", "Навигация")
	return TRUE

//Local orbital map for sector combat
/datum/local_orbital_map
	var/sector_x
	var/sector_y
	var/list/ships = list()
	var/list/obstacles = list() //asteroids, debris, etc
	var/map_size = 500 //500x500 local map
	
/datum/local_orbital_map/New(x, y)
	sector_x = x
	sector_y = y
	generate_obstacles()

/datum/local_orbital_map/proc/add_ship(datum/overmap/ship/controlled/ship)
	if(ship in ships)
		return
	ships += ship
	//Place ship at random position on local map
	ship.local_x = rand(50, map_size - 50)
	ship.local_y = rand(50, map_size - 50)

/datum/local_orbital_map/proc/remove_ship(datum/overmap/ship/controlled/ship)
	ships -= ship

/datum/local_orbital_map/proc/generate_obstacles()
	//Generate asteroids, debris based on sector type
	var/obstacle_count = rand(5, 15)
	for(var/i in 1 to obstacle_count)
		obstacles += list(list(
			"x" = rand(0, map_size),
			"y" = rand(0, map_size),
			"type" = "asteroid",
			"size" = rand(10, 30)
		))