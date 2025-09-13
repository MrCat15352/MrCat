//Admin verbs for orbital system

/client/verb/toggle_orbital_mode()
	set name = "Toggle Orbital Mode"
	set category = "Debug"
		
	to_chat(src, "Orbital mode toggle executed.")

/client/verb/orbital_map_admin()
	set name = "Open Orbital Map"
	set category = "Debug"
		
	SSorbits.orbital_map_tgui.ui_interact(mob)