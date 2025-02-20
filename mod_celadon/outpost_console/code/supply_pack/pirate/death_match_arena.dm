// MARK: ADMINISTRATOR ARENA

/datum/supply_pack/faction/death_match_arena/raznoe
	group = "Raznoe"

/datum/supply_pack/faction/death_match_arena/raznoe/sci_hardsuit
	name = "Science Hardsuit Crate"
	desc = "Contains one science hardsuit, designed to provide safety under advanced experimental conditions."
	cost = 100
	contains = list(/obj/item/clothing/suit/space/hardsuit/rd)
	crate_name = "science hardsuit crate"

/datum/supply_pack/faction/death_match_arena/raznoe/hardsuitswat
	name = "Nanotrasen MK2 SWAT hardsuit"
	desc = "Advanced MK2 SWAT hardsuit used by elite corporate assets. While it is bulky, slow and is missing a built in flashlight, it provides excellent protection against almost any weapon and is great for work in hazardous environments"
	contains = list(/obj/item/clothing/suit/space/hardsuit/swat/captain)
	cost = 100

/datum/supply_pack/faction/death_match_arena/raznoe/gorilla
	name = "Mob gorilla"
	desc = "Advanced MK2 SWAT hardsuit used by elite corporate assets. While it is bulky, slow and is missing a built in flashlight, it provides excellent protection against almost any weapon and is great for work in hazardous environments"
	contains = list(/mob/living/simple_animal/hostile/gorilla)
	cost = 100

/datum/supply_pack/faction/death_match_arena/raznoe/gorilla2
	name = "10 Mob gorilla"
	desc = "Advanced MK2 SWAT hardsuit used by elite corporate assets. While it is bulky, slow and is missing a built in flashlight, it provides excellent protection against almost any weapon and is great for work in hazardous environments"
	contains = list(/mob/living/simple_animal/hostile/gorilla = 10)
	cost = 100
