PROCESSING_SUBSYSTEM_DEF(starsectorfastprocess)
	name = "Starsector Fast Processing"
	wait = 0.02 SECONDS
	stat_tag = "SSFP"

/obj/machinery/porta_turret/starsector
	icon = 'mod_celadon/_storge_icons/icons/starsector/small_turrets.dmi'
	circuit = /obj/item/circuitboard/machine/turret/ruin
	faction = list("Turret")
	scan_range = 9
	req_ship_access = FALSE
	turret_respects_id = FALSE
	icon_state = "vulcan_cannon_off"
	base_icon_state = "vulcan_cannon"
	turret_flags = TURRET_FLAG_HOSTILE
	lethal = 1

/obj/machinery/porta_turret/starsector/vulcan_cannon
	name = "Vulcan Cannon"
	desc = "A juryrigged mishmash of a 9mm SMG and targetting system. Stand clear!"
	subsystem_type = /datum/controller/subsystem/processing/starsectorfastprocess
	integrity_failure = 0.6
	max_integrity = 180
	pixel_x = 4
	pixel_y = 4
	icon_state = "vulcan_cannon_lethal"
	base_icon_state = "vulcan_cannon"

	stun_projectile = /obj/projectile/bullet/vulcan_c9mm
	stun_projectile_sound = 'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_01.ogg'
	lethal_projectile = /obj/projectile/bullet/vulcan_c9mm
	lethal_projectile_sound = 'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_01.ogg'

	shot_delay = 8
	// scan_range = 9
	// shot_delay = 25
	burst_size = 10
	burst_delay = 6
	spread = 50

/obj/machinery/porta_turret/starsector/vulcan_cannon/Initialize()
	. = ..()
	stun_projectile_sound = pick('mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_01.ogg',
								'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_02.ogg',
								'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_03.ogg',
								'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_04.ogg',
								'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_05.ogg',
								'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_06.ogg')
	lethal_projectile_sound = pick('mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_01.ogg',
								'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_02.ogg',
								'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_03.ogg',
								'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_04.ogg',
								'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_05.ogg',
								'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_guns/vulcan_cannon_fire_01_06.ogg')

/obj/machinery/porta_turret/starsector/vulcan_cannon/minus
	stun_projectile = /obj/projectile/bullet/vulcan_c9mm_minus
	lethal_projectile = /obj/projectile/bullet/vulcan_c9mm_minus

/obj/machinery/porta_turret/starsector/vulcan_cannon/plus
	stun_projectile = /obj/projectile/bullet/vulcan_c9mm_plus
	lethal_projectile = /obj/projectile/bullet/vulcan_c9mm_plus

/obj/projectile/bullet/vulcan_c9mm
	name = "9x18mm bullet"
	damage = 2
	speed = BULLET_SPEED_HANDGUN
	bullet_identifier = "small bullet"

/obj/projectile/bullet/vulcan_c9mm_plus
	name = "9x18mm bullet"
	damage = 2
	armour_penetration = 20	//Больше дамага
	speed = BULLET_SPEED_HANDGUN
	bullet_identifier = "small bullet"

/obj/projectile/bullet/vulcan_c9mm_minus
	name = "9x18mm bullet"
	damage = 2
	armour_penetration = -20	//Больше брони
	speed = BULLET_SPEED_HANDGUN
	bullet_identifier = "small bullet"
