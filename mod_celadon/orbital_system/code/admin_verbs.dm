//Admin verbs for orbital system

/client/verb/toggle_orbital_mode()
	set name = "Toggle Orbital Mode"
	set category = "Debug"
		
	var/datum/overmap/ship/controlled/ship = SSovermap.get_overmap_object_by_location(usr)
	if(istype(ship))
		if(ship.in_orbital_mode)
			ship.exit_orbital_mode()
		else
			ship.enter_orbital_mode()
		return TRUE
	to_chat(src, "Orbital mode toggle executed.")

/client/verb/orbital_map_admin()
	set name = "Open Orbital Map"
	set category = "Debug"
		
	SSorbits.orbital_map_tgui.ui_interact(mob)