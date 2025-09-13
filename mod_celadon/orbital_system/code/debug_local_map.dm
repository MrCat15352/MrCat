//Debug for local orbital map opening

/client/verb/test_local_orbital()
	set name = "Test Local Orbital"
	set category = "Debug"
	
	var/datum/overmap/ship/controlled/ship = SSovermap.get_overmap_object_by_location(usr)
	if(!istype(ship))
		to_chat(src, "No ship found")
		return
	
	to_chat(src, "Ship: [ship.name]")
	to_chat(src, "In orbital mode: [ship.in_orbital_mode]")
	to_chat(src, "Has local map: [ship.current_local_map ? "YES" : "NO"]")
	
	if(ship.in_orbital_mode && ship.current_local_map)
		to_chat(src, "Opening local orbital interface...")
		var/datum/local_orbital_tgui/interface = new(ship)
		interface.ui_interact(usr)
	else
		to_chat(src, "Testing simple TGUI interface...")
		var/datum/test_tgui/test_interface = new()
		test_interface.ui_interact(usr)