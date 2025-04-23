/obj/machinery/porta_turret/starsector/tachyon_lance
	name = "Tachyon Lance"
	desc = "An abombination made out of the components of a Shredder and an automatic targetting system. Careful now."
	icon = 'mod_celadon/_storge_icons/icons/starsector/large_turrets.dmi'
	icon_state = "tachyon_lance_lethal"
	base_icon_state = "tachyon_lance"
	stun_projectile = /obj/projectile/energy/tachyon_lance
	stun_projectile_sound = 'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_energy/tachyon_lance_fire_01.ogg'
	lethal_projectile = /obj/projectile/energy/tachyon_lance
	lethal_projectile_sound = 'mod_celadon/_storge_sounds/sound/starsector/sfx_wpn_energy/tachyon_lance_fire_01.ogg'
	subsystem_type = /datum/controller/subsystem/processing/starsectorfastprocess
	integrity_failure = 0.6
	max_integrity = 500
	pixel_x = -20
	pixel_y = -20
	shot_delay = 50
	scan_range = 12
	burst_size = 1
	burst_delay = 10

/obj/projectile/energy/tachyon_lance
	name = "tesla orb"
	icon_state = "ice_2"
	damage = 50
	speed = 0.3
	var/shock_damage = 15

/obj/projectile/energy/tachyon_lance/on_hit(atom/target)
	. = ..()
	if(isliving(target))
		var/mob/living/victim = target
		victim.electrocute_act(shock_damage, src, siemens_coeff = 1, flags = SHOCK_NOSTUN | SHOCK_TESLA)
