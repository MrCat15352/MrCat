/mob/dead/observer/verb/open_orbit_ui()
	set name = "Показать орбиты"
	set category = "Призрак"
	#ifdef ORBITAL_SYSTEM_ENABLED
	SSorbits.orbital_map_tgui.ui_interact(src)
	#else
	to_chat(src, "Орбитальная система отключена.")
	#endif