/*
	Special elevator landmark that can teleport to a specific map
*/

/obj/effect/landmark/outpost/elevator/special
	name = "special outpost elevator landmark"
	/// The map file to teleport to (e.g. "centcom_ship.dmm")
	var/target_map
	/// The coordinates to teleport to on the target map
	var/target_x = 1
	var/target_y = 1
	var/target_z = 1

/obj/effect/landmark/outpost/elevator/special/Initialize(mapload)
	. = ..()
	// Register to intercept elevator platform movement
	RegisterSignal(SSdcs, COMSIG_GLOB_ELEVATOR_PLATFORM_TRAVEL, PROC_REF(intercept_elevator_travel))

/**
 * Intercepts elevator platform travel and redirects it to the target map if this landmark is involved
 *
 * Arguments:
 * * source - The source of the signal
 * * platform - The elevator platform that's traveling
 * * destination - The destination turf
 */
/obj/effect/landmark/outpost/elevator/special/proc/intercept_elevator_travel(datum/source, obj/structure/elevator_platform/platform, turf/destination)
	SIGNAL_HANDLER
	
	// Check if this is our elevator platform
	if(!platform || !platform.master_datum)
		return
		
	// Check if the platform is on the same turf as our landmark
	if(get_turf(platform) != get_turf(src))
		return
		
	// If we have a target map, teleport to it
	if(target_map)
		// Find the target z-level
		var/target_z_level = 0
		for(var/datum/map_template/template in SSmapping.map_templates)
			if(template.mappath == "_maps/[target_map]" || template.mappath == target_map)
				// Found the template, now find its z-level
				for(var/z_level in SSmapping.z_list)
					var/datum/space_level/S = SSmapping.z_list[z_level]
					if(S.name == template.name)
						target_z_level = z_level
						break
				break
				
		// If we found the z-level, teleport there
		if(target_z_level)
			var/turf/target_turf = locate(target_x, target_y, target_z_level)
			if(target_turf)
				// Teleport all contents of the platform to the target location
				for(var/atom/movable/thing as anything in platform.lift_load)
					if(QDELETED(thing))
						platform.lift_load -= thing
						continue
					thing.forceMove(target_turf)
				
				// Teleport the platform itself
				platform.forceMove(target_turf)
				return COMPONENT_CANCEL_ELEVATOR_TRAVEL