/obj/machinery/power/celadon
	name = "\improper Void Reactor"
	desc = "It's a debug reactor, contact coder if you see this."
	circuit = /obj/item/circuitboard/machine/autolathe
	var/sheets = 0
	var/max_sheets = 1
	var/sheet_name = ""
	var/sheet_path = /obj/item/stack/fuelcellMk17
	var/sheet_left = 0 // How much is left of the sheet
	var/time_per_sheet = 300
	var/current_heat = 0
	var/active = FALSE
	var/power_gen = 5000
	var/power_output = 1
	var/consumption = 1
	var/base_icon = "reactor"
	var/datum/looping_sound/generator/soundloop
	var/emagger //just gonna log this.
	interaction_flags_atom = INTERACT_ATOM_ATTACK_HAND | INTERACT_ATOM_UI_INTERACT | INTERACT_ATOM_REQUIRES_ANCHORED
	light_color = "#f88f39"
	layer = 5
	power_gen = 50000
	density = TRUE
	anchored = TRUE
	icon = 'mod_celadon/MK17_reactor/icon/reactor.dmi'
	base_icon = "reactor"
	icon_state = "reactor"

/obj/machinery/power/celadon/Initialize()
	. = ..()
	soundloop = new(list(src), active)

/obj/machinery/power/celadon/Destroy()
	QDEL_NULL(soundloop)
	return ..()

/obj/machinery/power/celadon/connect_to_network()
	if(!anchored)
		return FALSE
	. = ..()

/obj/machinery/power/celadon/proc/HasFuel() //Placeholder for fuel check.
	return TRUE

/obj/machinery/power/celadon/proc/UseFuel() //Placeholder for fuel use.
	return

/obj/machinery/power/celadon/proc/DropFuel()
	return

/obj/machinery/power/celadon/proc/handleInactive()
	return

/obj/machinery/power/celadon/proc/TogglePower()
	if(active)
		active = FALSE
		update_appearance()
		soundloop.stop()
	else if(HasFuel())
		active = TRUE
		START_PROCESSING(SSmachines, src)
		update_appearance()
		soundloop.start()

/obj/machinery/power/celadon/proc/overheat()
	message_admins("[src] [(obj_flags & EMAGGED) ? "Emagged by [emagger]" : "isn't emagged but somehow"] exploded at [ADMIN_VERBOSEJMP(src)]")

/obj/machinery/power/celadon/update_icon_state()
	icon_state = "[base_icon]_[active]"
	return ..()

/obj/machinery/power/celadon/process()
	if(active)
		if(!HasFuel() || !anchored)
			TogglePower()
			return
		if(powernet)
			add_avail(power_gen * power_output)
		UseFuel()
	else
		handleInactive()

/obj/machinery/power/celadon/examine(mob/user)
	. = ..()
	. += "It is[!active?"n't":""] running."

/obj/machinery/power/celadon/solarflareMk17
	name = "\improper Solarflare MK-17"
	desc = "The cutting-edge compact solarflare capable of unleashing powerful virtual solar flares, providing your spacecraft with unprecedented energy radiance in the digital cosmos."
	circuit = /obj/item/circuitboard/machine/solarflareMk17
	sheet_left = 0
	max_sheets = 1
	time_per_sheet = 300
	current_heat = 0
	light_color = "#f88f39"
	icon_state = "reactor"

/obj/machinery/power/celadon/solarflareMk17/Initialize()
	. = ..()
	if(anchored)
		connect_to_network()
	var/obj/S = sheet_path
	sheet_name = initial(S.name)
	update_brightness()

/obj/machinery/power/celadon/solarflareMk17/proc/update_brightness(mob/user)
	light_range = 1
	if(active)
		light_range = 3
	update_light()

/obj/machinery/power/celadon/solarflareMk17/proc/explosion(atom/epicenter, devastation_range, heavy_impact_range, light_impact_range, flash_range, adminlog = TRUE, ignorecap = FALSE, flame_range = 3, silent = FALSE, smoke = TRUE)
	. = SSexplosions.explode(arglist(args))

/obj/machinery/power/celadon/solarflareMk17/Destroy()
	if(active & obj_integrity < 1)
		explosion(src.loc, 3, 5, 2, 7)
		playsound(src, 'sound/effects/explosioncreak1.ogg', 100, TRUE, 10)
		return ..()
	DropFuel()
	return ..()

/obj/machinery/power/celadon/solarflareMk17/RefreshParts()
	var/temp_rating = 0
	var/consumption_coeff = 0
	if(active)
		overheat()
		qdel(src)
	for(var/obj/item/stock_parts/SP in component_parts)
		if(istype(SP, /obj/item/stock_parts/matter_bin))
			max_sheets = SP.rating
		else if(istype(SP, /obj/item/stock_parts/capacitor))
			temp_rating += SP.rating
			consumption_coeff += SP.rating
	power_gen = round(initial(power_gen) * (temp_rating / 2))
	consumption = consumption_coeff

/obj/machinery/power/celadon/solarflareMk17/examine(mob/user)
	. = ..()
	. += "<span class='notice'>The reactor has [sheets] units of [sheet_name] fuel left, producing [DisplayPower(power_gen)] per cycle. It is anchored to the ground.</span>"
	if(in_range(user, src) || isobserver(user))
		. += "<span class='notice'>The temperature display reads: Current heat is: \[<b>[(current_heat*5)+273] K</b>\].</span>"
		. += "<span class='notice'>Overload temperature is \[<b>[(255*5)+273] K</b>\].</span>"
		. += "<span class='notice'>The status display reads: Fuel efficiency increased by <b>[(consumption*100)-100]%</b>.</span>"


/obj/machinery/power/celadon/solarflareMk17/HasFuel()
	if(sheets >= 1 / (time_per_sheet / power_output) - sheet_left)
		return TRUE
	return FALSE

/obj/machinery/power/celadon/solarflareMk17/DropFuel()
	if(sheets)
		new sheet_path(drop_location(), sheets)
		sheets = 0

/obj/machinery/power/celadon/solarflareMk17/UseFuel()
	var/needed_sheets = 1 / (time_per_sheet * consumption / power_output)
	var/temp = min(needed_sheets, sheet_left)
	needed_sheets -= temp
	sheet_left -= temp
	sheets -= round(needed_sheets)
	needed_sheets -= round(needed_sheets)
	radiation_pulse(src, 15, 5, FALSE, FALSE)

	if (sheet_left <= 0 && sheets > 0)
		sheet_left = 1 - needed_sheets
		sheets--

	var/lower_limit = 56 + 2 * (power_output * power_output)
	var/upper_limit = 76 + 2 * (power_output * power_output)
	var/bias = (consumption * 2)
	var/rand1 = rand(7 + bias, 20 + bias)
	var/rand2 = rand(-1 * bias, -7 - bias)
	if (power_output == 4)
		upper_limit = 400
		bias = (consumption * 6)
	if (current_heat < lower_limit)
		current_heat += rand1
	else
		current_heat += rand(rand1, rand2)
		if (current_heat < 0)
			current_heat = 0
		if (current_heat > upper_limit)
			current_heat = upper_limit

	if (current_heat >= upper_limit - 25)
		playsound(src, 'sound/machines/alarm.ogg', 50, TRUE, 10)

	if (current_heat >= upper_limit)
		overheat()

	update_brightness()
	return

/obj/machinery/power/celadon/solarflareMk17/handleInactive()
	current_heat = max(current_heat - 15, 0)
	if(current_heat == 0)
		STOP_PROCESSING(SSmachines, src)
	update_brightness()

/obj/machinery/power/celadon/solarflareMk17/overheat()
	. =..()
	explosion(src.loc, 3, 5, 2, 7)
	qdel(src)

/obj/machinery/power/celadon/solarflareMk17/attackby(obj/item/O, mob/user, params)
	if(istype(O, sheet_path))
		var/obj/item/stack/addstack = O
		var/amount = min((max_sheets - sheets), addstack.amount)
		if(amount < 1)
			to_chat(user, "<span class='notice'>The [src.name] is full!</span>")
			return
		to_chat(user, "<span class='notice'>You add [amount] fuel cell to the [src.name].</span>")
		sheets += amount
		addstack.use(amount)
		return
	else if(!active)
		if(O.tool_behaviour == TOOL_SCREWDRIVER)
			panel_open = !panel_open
			O.play_tool_sound(src)
			if(panel_open)
				icon_state = "reactor"
				to_chat(user, "<span class='notice'>You open the access panel.</span>")
			else
				icon_state = "reactor_0"
				to_chat(user, "<span class='notice'>You close the access panel.</span>")
			return
		else if(default_deconstruction_crowbar(O))
			return
	return ..()

/obj/machinery/power/celadon/solarflareMk17/emag_act(mob/user)
	if(obj_flags & EMAGGED)
		return
	message_admins("[ADMIN_LOOKUPFLW(usr)] Has emagged [src] at [ADMIN_VERBOSEJMP(src)]")
	emagger = usr.ckey
	obj_flags |= EMAGGED
	emp_act(EMP_HEAVY)

/obj/machinery/power/celadon/solarflareMk17/attack_ai(mob/user)
	interact(user)

/obj/machinery/power/celadon/solarflareMk17/attack_paw(mob/user)
	interact(user)

/obj/machinery/power/celadon/solarflareMk17/ui_interact(mob/user, datum/tgui/ui)
	ui = SStgui.try_update_ui(user, src, ui)
	if(!ui)
		ui = new(user, src, "PortableGenerator", name)
		ui.open()

/obj/machinery/power/celadon/solarflareMk17/ui_data()
	var/data = list()

	data["active"] = active
	data["sheet_name"] = capitalize(sheet_name)
	data["sheets"] = sheets
	data["stack_percent"] = round(sheet_left * 100, 0.1)

	data["anchored"] = anchored
	data["connected"] = (powernet == null ? 0 : 1)
	data["ready_to_boot"] = anchored && HasFuel()
	data["power_generated"] = DisplayPower(power_gen)
	data["power_output"] = DisplayPower(power_gen * power_output)
	data["power_available"] = (powernet == null ? 0 : DisplayPower(avail()))
	data["current_heat"] = current_heat
	. =  data

/obj/machinery/power/celadon/solarflareMk17/ui_act(action, params)
	. = ..()
	if(.)
		return
	switch(action)
		if("toggle_power")
			TogglePower()
			. = TRUE

		if("eject")
			if(!active)
				DropFuel()
				. = TRUE

		if("lower_power")
			if (power_output > 1)
				power_output--
				. = TRUE

		if("higher_power")
			if (power_output < 4 || (obj_flags & EMAGGED))
				power_output++
				. = TRUE
