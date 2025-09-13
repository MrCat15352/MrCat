//Admin verbs for orbital system

/client/proc/toggle_orbital_mode()
	set name = "Toggle Orbital Mode"
	set category = "Admin.Game"
	
	if(!check_rights(R_ADMIN))
		return
		
	#ifdef ORBITAL_SYSTEM_ENABLED
	var/new_mode = !CONFIG_GET(flag/orbital_mode_enabled)
	CONFIG_SET(flag/orbital_mode_enabled, new_mode)
	
	message_admins("[key_name_admin(usr)] [new_mode ? "включил" : "отключил"] орбитальный режим навигации.")
	log_admin("[key_name(usr)] toggled orbital mode to [new_mode]")
	
	to_chat(src, "Орбитальный режим [new_mode ? "включен" : "отключен"].")
	#else
	to_chat(src, "Орбитальная система не скомпилирована.")
	#endif

/client/proc/orbital_map_admin()
	set name = "Open Orbital Map"
	set category = "Admin.Game"
	
	if(!check_rights(R_ADMIN))
		return
		
	#ifdef ORBITAL_SYSTEM_ENABLED
	SSorbits.orbital_map_tgui.ui_interact(mob)
	#else
	to_chat(src, "Орбитальная система не скомпилирована.")
	#endif