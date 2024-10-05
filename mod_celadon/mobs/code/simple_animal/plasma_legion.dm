/mob/living/simple_animal/hostile/asteroid/hivelord/legion/crystal/plasma
	icon = 'mod_celadon/_storge_icons/icons/mob/plasma_legion.dmi'
	brood_type = /mob/living/simple_animal/hostile/asteroid/hivelordbrood/legion/crystal/plasma

/mob/living/simple_animal/hostile/asteroid/hivelordbrood/legion/crystal/plasma
	icon = 'mod_celadon/_storge_icons/icons/mob/plasma_legion.dmi'
	move_to_delay = 1

/obj/projectile/goliath/plasma
	icon = 'mod_celadon/_storge_icons/icons/mob/projectile.dmi'

/obj/effect/temp_visual/goliath_tentacle/crystal/plasma
	icon = 'mod_celadon/_storge_icons/icons/mob/32x64.dmi'

/mob/living/simple_animal/hostile/asteroid/hivelordbrood/legion/crystal/plasma/death(gibbed)
	for(var/i in 0 to 5)
		var/obj/projectile/P = new /obj/projectile/goliath/plasma(get_turf(src))
		P.preparePixelProjectile(get_step(src, pick(GLOB.alldirs)), get_turf(src))
		P.firer = source
		P.fire(i*(360/5))
	return ..()

<<<<<<< HEAD
/obj/projectile/goliath/plasma/on_hit(atom/target, blocked)
	. = ..()
	var/turf/turf_hit = get_turf(target)
	new /obj/effect/temp_visual/goliath_tentacle/crystal/plasma(turf_hit,firer)
=======
/obj/item/organ/regenerative_core/legion/crystal/plasma
	icon = 'mod_celadon/_storge_icons/icons/obj/plasma_heart.dmi'

/mob/living/simple_animal/hostile/big_plasma
	name = "Legate"
	desc = "A rare and incredibly dangerous legion mutation, forming from a plethora of legion joined in union around a young necropolis spire. It's looking particularly self-confident."
	icon = 'mod_celadon/_storge_icons/icons/mob/64x64mehafauna.dmi'
	icon_state = "plasma"
	icon_living = "plasma"
	icon_dead = "plasma"
	health_doll_icon = "plasma"
	health = 500
	maxHealth = 500
	melee_damage_lower = 30
	melee_damage_upper = 30
	anchored = FALSE
	AIStatus = AI_ON
	obj_damage = 150
	stop_automated_movement = FALSE
	wander = TRUE
	attack_verb_continuous = "brutally slams"
	attack_verb_simple = "brutally slam"
	layer = MOB_LAYER
	del_on_death = TRUE
	sentience_type = SENTIENCE_BOSS
	loot = list(/obj/item/organ/regenerative_core/legion/crystal/plasma = 3, /obj/effect/mob_spawn/human/corpse/damaged/legioninfested = 5, /obj/effect/mob_spawn/human/corpse/damaged/legioninfested = 5, /obj/effect/mob_spawn/human/corpse/damaged/legioninfested = 5)
	atmos_requirements = list("min_oxy" = 0, "max_oxy" = 0, "min_tox" = 0, "max_tox" = 0, "min_co2" = 0, "max_co2" = 0, "min_n2" = 0, "max_n2" = 0)
	minbodytemp = 0
	maxbodytemp = INFINITY
	move_to_delay = 7
	vision_range = 4
	aggro_vision_range = 4
	speed = 8
	faction = list("mining")
	weather_immunities = list("lava","ash")
	environment_smash = ENVIRONMENT_SMASH_RWALLS
	see_in_dark = 8
	lighting_alpha = LIGHTING_PLANE_ALPHA_MOSTLY_INVISIBLE

/mob/living/simple_animal/hostile/big_plasma/death(gibbed)
	move_force = MOVE_FORCE_DEFAULT
	move_resist = MOVE_RESIST_DEFAULT
	pull_force = PULL_FORCE_DEFAULT
	visible_message("<span class='userwarning'>[src] falls over with a mighty crash, the remaining legions within it falling apart!</span>")
	new /mob/living/simple_animal/hostile/asteroid/hivelord/legion/crystal_plasma(loc)
	new /mob/living/simple_animal/hostile/asteroid/hivelord/legion/crystal_plasma(loc)
	new /mob/living/simple_animal/hostile/asteroid/hivelord/legion/crystal_plasma(loc)
	..(gibbed)

/mob/living/simple_animal/hostile/big_plasma/Initialize()
	.=..()
	AddComponent(/datum/component/spawner, list(/mob/living/simple_animal/hostile/asteroid/hivelord/legion/crystal_plasma), 200, faction, "peels itself off from", 3)

/mob/living/simple_animal/hostile/big_legion
	icon = 'mod_celadon/_storge_icons/icons/mob/64x64mehafauna.dmi'
>>>>>>> 8470a82a8416b0a94f3e9d155352da08c5f0507d
