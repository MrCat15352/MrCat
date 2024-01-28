//Copy-pasted kepori and lizard stuff
/datum/species/tajaran
	name = "\improper tajaran"
	id = SPECIES_TAJARAN
	default_color = "424242"
	species_traits = list(LIPS)
	inherent_traits = list(TRAIT_NIGHT_VISION)
	mutant_bodyparts = list("tajaran_body", "tajaran_tail")
	mutanttongue = /obj/item/organ/tongue/tajaran
	mutant_organs = list(/obj/item/organ/tail/tajaran)
	default_features = list("mcolor" = "0F0", "tajaran_tail" = "tajtail", "face_markings" = "None", "body_markings" = "None", "body_size" = "Normal")
	disliked_food = VEGETABLES | FRUIT | GRAIN | GROSS
	liked_food = MEAT | RAW | DAIRY
	changesource_flags = MIRROR_BADMIN | WABBAJACK | MIRROR_PRIDE | MIRROR_MAGIC | RACE_SWAP | ERT_SPAWN | SLIME_EXTRACT
	attack_verb = "slash"
	attack_sound = 'sound/weapons/slash.ogg'
	miss_sound = 'sound/weapons/slashmiss.ogg'
	meat = /obj/item/reagent_containers/food/snacks/meat/slab/human/mutant/lizard //Needs draw sprite meat
//	heatmod = 0.8
//	coldmod = 1.2
//	bodytemp_normal = HUMAN_BODYTEMP_NORMAL + 30
//	bodytemp_heat_damage_limit = HUMAN_BODYTEMP_HEAT_DAMAGE_LIMIT - 10
//	bodytemp_cold_damage_limit = HUMAN_BODYTEMP_COLD_DAMAGE_LIMIT + 30
	mutanttongue = /obj/item/organ/tongue/tajaran
	species_language_holder = /datum/language_holder/tajaran
	loreblurb = "The Tajaran race is a species of feline-like bipeds hailing from the planet of Ahdomai in the \
	S'randarr system. They have been brought up into the space age by the Humans and Skrell, and have been \
	influenced heavily by their long history of Slavemaster rule. They have a structured, clan-influenced way \
	of family and politics. They prefer colder environments, and speak a variety of languages, mostly Siik'Maas, \
	using unique inflections their mouths form."

	ass_image = 'icons/ass/asscat.png'

	bodytype = BODYTYPE_TAJARAN

	species_chest = /obj/item/bodypart/chest/tajaran
	species_head = /obj/item/bodypart/head/tajaran
	species_l_arm = /obj/item/bodypart/l_arm/tajaran
	species_r_arm = /obj/item/bodypart/r_arm/tajaran
	species_l_leg = /obj/item/bodypart/leg/left/tajaran
	species_r_leg = /obj/item/bodypart/leg/right/tajaran

/datum/species/tajaran/random_name(gender,unique,lastname) //hhhhhssssss ПЕРЕДЕЛАТЬ
	if(unique)
		return random_unique_tajaran_name()
	return tajaran_name()

/*
/datum/species/kepori/New()
	. = ..()
	// This is in new because "[HEAD_LAYER]" etc. is NOT a constant compile-time value. For some reason.
	// Why not just use HEAD_LAYER? Well, because HEAD_LAYER is a number, and if you try to use numbers as indexes,
	// BYOND will try to make it an ordered list. So, we have to use a string. This is annoying, but it's the only way to do it smoothly.
	offset_clothing = list(
		"[HEAD_LAYER]" = list("[NORTH]" = list("x" = 0, "y" = -4), "[EAST]" = list("x" = 4, "y" = -4), "[SOUTH]" = list("x" = 0, "y" = -4), "[WEST]" = list("x" =  -4, "y" = -4)),
		"[GLASSES_LAYER]" = list("[NORTH]" = list("x" = 0, "y" = -4), "[EAST]" = list("x" = 4, "y" = -4), "[SOUTH]" = list("x" = 0, "y" = -4), "[WEST]" = list("x" =  -4, "y" = -4)),
		"[FACEMASK_LAYER]" = list("[NORTH]" = list("x" = 0, "y" = -5), "[EAST]" = list("x" = 4, "y" = -5), "[SOUTH]" = list("x" = 0, "y" = -5), "[WEST]" = list("x" =  -4, "y" = -5)),
	)*/

/*
/datum/species/kepori/can_equip(obj/item/I, slot, disable_warning, mob/living/carbon/human/H, bypass_equip_delay_self, swap)
	if(..()) //If it already fits, then it's fine.
		return TRUE
	if(slot == ITEM_SLOT_MASK)
		if(H.wear_mask && !swap)
			return FALSE
		if(I.w_class > WEIGHT_CLASS_SMALL)
			return FALSE
		if(!H.get_bodypart(BODY_ZONE_HEAD))
			return FALSE
		return equip_delay_self_check(I, H, bypass_equip_delay_self)

/datum/species/kepori/on_species_gain(mob/living/carbon/C, datum/species/old_species, pref_load)
	..()
	if(ishuman(C))
		keptackle = new
		keptackle.Grant(C)

/datum/species/kepori/on_species_loss(mob/living/carbon/human/C, datum/species/new_species, pref_load)
	if(keptackle)
		keptackle.Remove(C)
	qdel(C.GetComponent(/datum/component/tackler))
	..()


/datum/action/innate/keptackle
	name = "Pounce"
	desc = "Ready yourself to pounce."
	check_flags = AB_CHECK_CONSCIOUS
	button_icon_state = "tackle"
	icon_icon = 'icons/obj/clothing/gloves.dmi'
	background_icon_state = "bg_alien"

/datum/action/innate/keptackle/Activate()
	var/mob/living/carbon/human/H = owner
	var/datum/species/kepori/kep = H.dna.species
	if(H.GetComponent(/datum/component/tackler))
		qdel(H.GetComponent(/datum/component/tackler))
		to_chat(H, "<span class='notice'>You relax, no longer ready to pounce.</span>")
		return
	H.AddComponent(/datum/component/tackler, stamina_cost= kep.tackle_stam_cost, base_knockdown= kep.base_knockdown, range= kep.tackle_range, speed= kep.tackle_speed, skill_mod= kep.skill_mod, min_distance= kep.min_distance)
	H.visible_message("<span class='notice'>[H] gets ready to pounce!</span>", \
		"<span class='notice'>You ready yourself to pounce!</span>", null, COMBAT_MESSAGE_RANGE)*/
