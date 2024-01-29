//Copy-pasted kepori and lizard stuff
/datum/species/tajaran
	name = "\improper tajaran"
	id = SPECIES_TAJARAN
	loreblurb = "The Tajaran race is a species of feline-like bipeds hailing from the planet of Ahdomai in the \
	S'randarr system. They have been brought up into the space age by the Humans and Skrell, and have been \
	influenced heavily by their long history of Slavemaster rule. They have a structured, clan-influenced way \
	of family and politics. They prefer colder environments, and speak a variety of languages, mostly Siik'Maas, \
	using unique inflections their mouths form."

	changesource_flags = MIRROR_BADMIN | WABBAJACK | MIRROR_PRIDE | MIRROR_MAGIC | RACE_SWAP | ERT_SPAWN | SLIME_EXTRACT

	disliked_food = VEGETABLES | FRUIT | GRAIN | GROSS
	liked_food = MEAT | RAW | DAIRY

	attack_verb = "slash"
	attack_sound = 'sound/weapons/slash.ogg'
	miss_sound = 'sound/weapons/slashmiss.ogg'

	species_traits = list(EYECOLOR, LIPS, EMOTE_OVERLAY, MUTCOLORS, MUTCOLORS_SECONDARY)
	inherent_traits = list(TRAIT_NIGHT_VISION)

	mutant_bodyparts = list("tajaran_ears", "tajaran_hair", "tajaran_head_markings_list", "tajaran_face_markings", "tajaran_body_markings", "tajaran_tail")
	default_features = list(
		"mcolor" = "0F0",
		"tajaran_ears" = "Plain",
		"tajaran_hair" = "Bob", 			//for fun
		"tajaran_head_markings_list" = "none",
		"tajaran_face_markings" = "None",
		"tajaran_body_markings" = "None",
		"tajaran_tail" = "tajtail",
		"body_size" = "Normal"
		)

	default_color = "424242"

	heatmod = 0.8
	coldmod = 1.2
	bodytemp_normal = HUMAN_BODYTEMP_NORMAL + 30
	bodytemp_heat_damage_limit = (HUMAN_BODYTEMP_NORMAL + 30) + 10
	bodytemp_cold_damage_limit = (HUMAN_BODYTEMP_NORMAL + 30) - 40

	meat = /obj/item/reagent_containers/food/snacks/meat/slab/human/mutant/tajaran 	//нарисовать/спиздить спрайт к нему
	//skinned_type = /obj/item/stack/sheet/animalhide/tajaran						//нужно сделать кожу из таяран и нарисовать/спиздить спрайт к нему

	species_language_holder = /datum/language_holder/tajaran

	ass_image = 'icons/ass/asscat.png'

	mutanttongue = /obj/item/organ/tongue/tajaran
	mutant_organs = list(
		/obj/item/organ/tail/tajaran,
		/obj/item/organ/ears/tajaran		//нужно отделить уши от головы. и можно кинуть их в тот же файл. потом в органе прописать путь к файлу + имя файла
		)

	bodytype = BODYTYPE_TAJARAN
	species_chest = /obj/item/bodypart/chest/tajaran
	species_head = /obj/item/bodypart/head/tajaran
	species_l_arm = /obj/item/bodypart/l_arm/tajaran
	species_r_arm = /obj/item/bodypart/r_arm/tajaran
	species_l_leg = /obj/item/bodypart/leg/left/tajaran
	species_r_leg = /obj/item/bodypart/leg/right/tajaran

	species_robotic_chest = /obj/item/bodypart/chest/robot
	species_robotic_head = /obj/item/bodypart/head/robot
	species_robotic_l_arm = /obj/item/bodypart/l_arm/robot/surplus
	species_robotic_r_arm = /obj/item/bodypart/r_arm/robot/surplus
	species_robotic_l_leg = /obj/item/bodypart/leg/left/robot/surplus
	species_robotic_r_leg = /obj/item/bodypart/leg/right/robot/surplus


/datum/species/tajaran/random_name(gender,unique,lastname)
	//code by @valtor0
	var/static/list/tajaran_female_endings_list = list("и","а","о","е","й","ь") // Customise this with ru_name_syllables changes.
	var/list/ru_name_syllables = list("кан","тай","кир","раи","кии","мир","кра","тэк","нал","вар","хар","марр","ран","дарр", \
	"мирк","ири","дин","манг","рик","зар","раз","кель","шера","тар","кей","ар","но","маи","зир","кер","нир","ра",\
	"ми","рир","сей","эка","гир","ари","нэй","нре","ак","таир","эрай","жин","мра","зур","рин","сар","кин","рид","эра","ри","эна")
	var/apostrophe = "’"
	var/new_name = ""
	var/full_name = ""

	for(var/i = 0; i<2; i++)
		for(var/x = rand(1,2); x>0; x--)
			new_name += pick_n_take(ru_name_syllables)
		new_name += apostrophe
		apostrophe = ""
	full_name = "[capitalize(lowertext(new_name))]"
	if(gender == FEMALE)
		var/ending = copytext(full_name, -2)
		if(!(ending in tajaran_female_endings_list))
			full_name += "а"
	if(prob(75))
		full_name += " [pick(list("Хадии","Кайтам","Жан-Хазан","Нъярир’Ахан"))]"
	else if(prob(80))
		full_name += " [pick(list("Энай-Сэндай","Наварр-Сэндай","Року-Сэндай","Шенуар-Сэндай"))]"
	return full_name

/* эта шляпа нужна, если мы будем давать какие-то кнопки таяранам, которые слева сверху, по типу "вкл/выкл фонарик ПДА"

/datum/species/tajaran/on_species_gain(mob/living/carbon/C, datum/species/old_species, pref_load)
	..()
	if(ishuman(C))
*/

/* антипод функции выше - убираем кнопки\плюшки таяранам

/datum/species/kepori/on_species_loss(mob/living/carbon/human/C, datum/species/new_species, pref_load)
	if(keptackle)
		keptackle.Remove(C)
	qdel(C.GetComponent(/datum/component/tackler))
	..()
*/
