/datum/language/tajaran
	name = "Siik'tajr"
	desc = "The traditionally employed tongue of Ahdomai, composed of expressive yowls and chirps. Native to the Tajaran."
	speech_verb = "mrowls"
	ask_verb = "mrowls"
	exclaim_verbs = list("yowls")
	key = "j"
	flags = RESTRICTED
	syllables = list("rr","rr","tajr","kir","raj","kii","mir","kra","ahk","nal","vah","khaz","jri","ran","darr", \
	"mi","jri","dynh","manq","rhe","zar","rrhaz","kal","chur","eech","thaa","dra","jurl","mah","sanu","dra","ii'r", \
	"ka","aasi","far","wa","baq","ara","qara","zir","sam","mak","hrar","nja","rir","khan","jun","dar","rik","kah", \
	"hal","ket","jurl","mah","tul","cresh","azu","ragh")

/datum/language/tajaran/get_random_name(gender) //code by @valtor0
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
	//20% for "Sendai" clan; 18,75% (75%) for other regular clan; 5% for names without clan.
	if(prob(75))
		full_name += " [pick(list("Хадии","Кайтам","Жан-Хазан","Нъярир’Ахан"))]"
	else if(prob(80))
		full_name += " [pick(list("Энай-Сэндай","Наварр-Сэндай","Року-Сэндай","Шенуар-Сэндай"))]"
	return full_name
