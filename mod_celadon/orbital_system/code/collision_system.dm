//Collision system for local orbital maps

/datum/local_orbital_map/proc/check_ship_collisions(datum/overmap/ship/controlled/ship)
	//Check obstacle collisions
	for(var/list/obstacle in obstacles)
		var/distance = sqrt((ship.local_x - obstacle["x"])**2 + (ship.local_y - obstacle["y"])**2)
		if(distance < obstacle["size"] + 15) //ship size
			//Collision with obstacle
			ship.local_vel_x *= -0.5
			ship.local_vel_y *= -0.5
			//Push ship away
			var/push_x = (ship.local_x - obstacle["x"]) / distance * 10
			var/push_y = (ship.local_y - obstacle["y"]) / distance * 10
			ship.local_x += push_x
			ship.local_y += push_y
			
			//Damage ship
			ship.take_damage(10)
	
	//Check ship-to-ship collisions
	for(var/datum/overmap/ship/controlled/other_ship in ships)
		if(other_ship == ship)
			continue
		
		var/distance = sqrt((ship.local_x - other_ship.local_x)**2 + (ship.local_y - other_ship.local_y)**2)
		if(distance < 30) //collision distance
			//Ships collided
			var/push_force = 15
			var/push_x = (ship.local_x - other_ship.local_x) / distance * push_force
			var/push_y = (ship.local_y - other_ship.local_y) / distance * push_force
			
			ship.local_x += push_x
			ship.local_y += push_y
			other_ship.local_x -= push_x
			other_ship.local_y -= push_y
			
			//Exchange velocities (simplified)
			var/temp_vel_x = ship.local_vel_x
			var/temp_vel_y = ship.local_vel_y
			ship.local_vel_x = other_ship.local_vel_x * 0.8
			ship.local_vel_y = other_ship.local_vel_y * 0.8
			other_ship.local_vel_x = temp_vel_x * 0.8
			other_ship.local_vel_y = temp_vel_y * 0.8
			
			//Damage both ships
			ship.take_damage(20)
			other_ship.take_damage(20)

/datum/overmap/ship/controlled/proc/take_damage(amount)
	//Placeholder for ship damage system
	log_world("Корабль [name] получил повреждения!")
	//TODO: Implement actual ship damage system