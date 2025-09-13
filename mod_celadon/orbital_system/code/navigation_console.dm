//Navigation console that can switch between overmap and orbital modes

/obj/machinery/computer/navigation
	name = "навигационная консоль"
	desc = "Консоль для навигации в космосе."
	icon_screen = "navigation"
	circuit = /obj/item/circuitboard/computer/navigation

/obj/machinery/computer/navigation/ui_interact(mob/user, datum/tgui/ui)
	#ifdef ORBITAL_SYSTEM_ENABLED
	if(SSovermap.use_orbital_mode())
		SSorbits.orbital_map_tgui.ui_interact(user)
		return
	#endif
	// Fallback to overmap interface
	to_chat(user, "Орбитальная система недоступна. Используйте стандартную навигацию.")

/obj/item/circuitboard/computer/navigation
	name = "Navigation Console"
	build_path = /obj/machinery/computer/navigation