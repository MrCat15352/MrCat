/obj/item/stack/fuelcellMk17
	name = "Fuel Cell MK-17"
	desc = "Electrochemical device used to generate electricity from fuel. A fuel cell can be used to reactor 'Solarflare MK-17' because it provides quick access to fuel and allows for efficient production of electricity."
	icon = 'mod_celadon/MK17_reactor/icon/fuelcell.dmi'
	icon_state = "fuelcell"
	item_state = "fuelcell	"
	lefthand_file = 'mod_celadon/MK17_reactor/icon/fuelcell_lefthand.dmi'
	righthand_file = 'mod_celadon/MK17_reactor/icon/fuelcell_righthand.dmi'
	w_class = WEIGHT_CLASS_BULKY
	full_w_class = WEIGHT_CLASS_BULKY
	layer = 3.5
	max_amount = 1
	throwforce = 1
	throw_speed = 1
	throw_range = 1
	force = 0

/obj/item/stack/fuelcellMk17/Initialize()
	. = ..()

/obj/item/stack/fuelcellMk17/attackby(obj/item/W as obj, mob/user as mob, params)
	if(W.get_temperature() > 300)//If the temperature of the object is over 300, then ignite
		var/turf/T = get_turf(src)
		message_admins("Fuel Cell MK-17 ignited by [ADMIN_LOOKUPFLW(user)] in [ADMIN_VERBOSEJMP(T)]")
		log_game("Fuel Cell MK-17 ignited by [key_name(user)] in [AREACOORD(T)]")
		fire_act(W.get_temperature())
	else
		return ..()

/obj/item/stack/fuelcellMk17/fire_act(exposed_temperature, exposed_volume)
	atmos_spawn_air("plasma=[amount*10];TEMP=[exposed_temperature]")
	qdel(src)
