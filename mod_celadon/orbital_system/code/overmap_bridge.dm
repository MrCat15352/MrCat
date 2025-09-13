//Bridge between overmap and orbital systems

/datum/controller/subsystem/overmap/proc/use_orbital_mode()
	#ifdef ORBITAL_SYSTEM_ENABLED
	return TRUE
	#else
	return FALSE
	#endif

/datum/controller/subsystem/overmap/proc/get_navigation_interface(mob/user)
	#ifdef ORBITAL_SYSTEM_ENABLED
	if(use_orbital_mode())
		SSorbits.orbital_map_tgui.ui_interact(user)
		return TRUE
	#endif
	return FALSE