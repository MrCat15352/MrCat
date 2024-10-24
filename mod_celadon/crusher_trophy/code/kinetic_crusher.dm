/*********************Mining Hammer****************/
/obj/item/kinetic_crusher
	var/list/trophies = list()
	var/trophiesnumber = 0	// Починка от Ганзы

/obj/item/kinetic_crusher/Destroy()
	QDEL_LIST(trophies)
	return ..()

/obj/item/kinetic_crusher/attackby(obj/item/I, mob/living/user)
	if(I.tool_behaviour == TOOL_CROWBAR)
		if(LAZYLEN(trophies))
			var/list/choose_options = list()
			for(var/obj/item/crusher_trophy/T in trophies)
				choose_options += list(T.name = image(icon = T.icon, icon_state = T.icon_state))
			var/picked_option = show_radial_menu(user, src, choose_options, radius = 38, require_near = TRUE)
			if(picked_option)
				to_chat(user, "<span class='notice'>You remove [picked_option].</span>")
				I.play_tool_sound(src)
				for(var/obj/item/crusher_trophy/T in trophies)
					if(T.name == picked_option)
						T.remove_from(src, user)
		else
			to_chat(user, "<span class='warning'>There are no trophies on [src].</span>")
	else if(istype(I, /obj/item/crusher_trophy))
		var/obj/item/crusher_trophy/T = I
		T.add_to(src, user)
	else
		return ..()

//trophies
/obj/item/crusher_trophy
	name = "tail spike"
	desc = "A strange spike with no usage."
	icon = 'icons/obj/lavaland/artefacts.dmi'
	icon_state = "tail_spike"
	var/bonus_value = 10 //if it has a bonus effect, this is how much that effect is
	var/denied_type = /obj/item/crusher_trophy

/obj/item/crusher_trophy/examine(mob/living/user)
	. = ..()
	. += "<span class='notice'>Causes [effect_desc()] when attached to a kinetic crusher.</span>"

/obj/item/crusher_trophy/proc/effect_desc()
	return "errors"

/obj/item/crusher_trophy/attackby(obj/item/A, mob/living/user)
	if(istype(A, /obj/item/kinetic_crusher))
		add_to(A, user)
	else
		..()

/obj/item/crusher_trophy/proc/add_to(obj/item/kinetic_crusher/H, mob/living/user)
	for(var/t in H.trophies)
		var/obj/item/crusher_trophy/T = t
		if(istype(T, denied_type) || istype(src, T.denied_type))
			to_chat(user, "<span class='warning'>You can't seem to attach [src] to [H]. Maybe remove a few trophies?</span>")
			return FALSE
	if(!user.transferItemToLoc(src, H))
		return
	H.trophies += src
	to_chat(user, "<span class='notice'>You attach [src] to [H].</span>")
	H.trophiesnumber = H.trophies.len	// Починка пустого списка от Ганзы
	return TRUE

/obj/item/crusher_trophy/proc/remove_from(obj/item/kinetic_crusher/H, mob/living/user)
	forceMove(get_turf(H))
	H.trophies -= src
	H.trophiesnumber = H.trophies.len	// Починка пустого списка от Ганзы
	return TRUE

/obj/item/crusher_trophy/proc/on_melee_hit(mob/living/target, mob/living/user) //the target and the user
/obj/item/crusher_trophy/proc/on_projectile_fire(obj/projectile/destabilizer/marker, mob/living/user) //the projectile fired and the user
/obj/item/crusher_trophy/proc/on_mark_application(mob/living/target, datum/status_effect/crusher_mark/mark, had_mark) //the target, the mark applied, and if the target had a mark before
/obj/item/crusher_trophy/proc/on_mark_detonation(mob/living/target, mob/living/user) //the target and the user

//goliath
/obj/item/crusher_trophy/goliath_tentacle
	name = "goliath tentacle"
	desc = "A sliced-off goliath tentacle."
	icon_state = "goliath_tentacle"
	denied_type = /obj/item/crusher_trophy/goliath_tentacle
	bonus_value = 5
	var/missing_health_ratio = 0.1
	var/missing_health_desc = 10

/obj/item/crusher_trophy/goliath_tentacle/effect_desc()
	return "waveform collapse to do <b>[bonus_value]</b> more damage for every <b>[missing_health_desc]</b> health you are missing"

/obj/item/crusher_trophy/goliath_tentacle/on_mark_detonation(mob/living/target, mob/living/user)
	var/missing_health = user.maxHealth - user.health
	missing_health *= missing_health_ratio //bonus is active at all times, even if you're above 90 health
	missing_health *= bonus_value //multiply the remaining amount by bonus_value
	if(missing_health > 0)
		target.adjustBruteLoss(missing_health) //and do that much damage

//ancient goliath
/obj/item/crusher_trophy/elder_tentacle
	name = "elder tentacle"
	desc = "The barbed tip of a tentacle sliced from an incredibly ancient goliath."
	icon_state = "elder_tentacle"
	denied_type = /obj/item/crusher_trophy/elder_tentacle
	bonus_value = 3
	var/missing_health_ratio = 0.1
	var/missing_health_desc = 5
	icon = 'icons/obj/lavaland/elite_trophies.dmi'

/obj/item/crusher_trophy/elder_tentacle/examine(mob/user)
	. = ..()
	. += "<span class='notice'>Suitable as a trophy for a proto-kinetic crusher.</span>"

/obj/item/crusher_trophy/elder_tentacle/effect_desc()
	return "waveform collapse to do <b>[bonus_value]</b> more damage for every <b>[missing_health_desc]</b> health you are missing"

/obj/item/crusher_trophy/elder_tentacle/on_mark_detonation(mob/living/target, mob/living/user)
	var/missing_health = user.maxHealth - user.health
	missing_health *= missing_health_ratio //bonus is active at all times, even if you're above 90 health
	missing_health *= bonus_value //multiply the remaining amount by bonus_value
	if(missing_health > 0)
		target.adjustBruteLoss(missing_health) //and do that much damage

//crystal goliath
/obj/item/crusher_trophy/goliath_crystal
	name = "goliath crystal"
	desc = "A crystal ripped off from a goliath infected by the strange crystals. You can see the original skin of the goliath deeply embeded in it."
	icon_state = "goliath_crystal"
	denied_type = /obj/item/crusher_trophy/elder_tentacle
	bonus_value = 4
	var/missing_health_ratio = 0.1
	var/missing_health_desc = 5

/obj/item/crusher_trophy/goliath_crystal/effect_desc()
	return "waveform collapse to stun creatures for <b>[bonus_value*0.1]</b> second\s"

/obj/item/crusher_trophy/goliath_crystal/on_mark_detonation(mob/living/simple_animal/target, mob/living/user)
	if(!ishostile(target))
		return
	var/mob/living/simple_animal/hostile/hostile_target = target
	var/hostile_ai_status = hostile_target.AIStatus
	hostile_target.AIStatus = AI_OFF
	addtimer(VARSET_CALLBACK(hostile_target, AIStatus, hostile_ai_status), bonus_value*0.1 SECONDS)

//watcher
/obj/item/crusher_trophy/watcher_wing
	name = "watcher wing"
	desc = "A wing ripped from a watcher."
	icon_state = "watcher_wing"
	denied_type = /obj/item/crusher_trophy/watcher_wing
	bonus_value = 5

/obj/item/crusher_trophy/watcher_wing/effect_desc()
	return "waveform collapse to prevent certain creatures from using certain attacks for <b>[bonus_value*0.1]</b> second\s"

/obj/item/crusher_trophy/watcher_wing/on_mark_detonation(mob/living/target, mob/living/user)
	if(ishostile(target))
		var/mob/living/simple_animal/hostile/H = target
		if(H.ranged) //briefly delay ranged attacks
			if(H.ranged_cooldown >= world.time)
				H.ranged_cooldown += bonus_value
			else
				H.ranged_cooldown = bonus_value + world.time

//magmawing watcher
/obj/item/crusher_trophy/magma_wing
	name = "magmatic sinew"
	desc = "A fuming organ, dropped by beings hotter then lava."
	icon_state = "magma_wing"
	denied_type = /obj/item/crusher_trophy/magma_wing
	gender = NEUTER
	bonus_value = 5
	var/deadly_shot = FALSE

/obj/item/crusher_trophy/magma_wing/effect_desc()
	return "waveform collapse to make the next magnetic pulse deal <b>[bonus_value]</b> damage"

/obj/item/crusher_trophy/magma_wing/examine(mob/user)
	. = ..()
	. += "<span class='notice'>Suitable as a trophy for a proto-kinetic crusher.</span>"

/obj/item/crusher_trophy/magma_wing/on_projectile_fire(obj/projectile/destabilizer/marker, mob/living/user)
	if(deadly_shot)
		marker.name = "superheated [marker.name]"
		marker.icon_state = "lava"
		marker.damage = bonus_value
		marker.nodamage = FALSE
		marker.speed = 2
		deadly_shot = FALSE

/obj/item/crusher_trophy/magma_wing/on_mark_detonation(mob/living/target, mob/living/user)
	deadly_shot = TRUE
	addtimer(CALLBACK(src, PROC_REF(reset_deadly_shot)), 300, TIMER_UNIQUE|TIMER_OVERRIDE)

/obj/item/crusher_trophy/magma_wing/proc/reset_deadly_shot()
	deadly_shot = FALSE

//icewing watcher
/obj/item/crusher_trophy/ice_wing
	name = "frigid sinew"
	desc = "A carefully-preserved freezing organ, dropped by chilling beings."
	icon_state = "ice_wing"
	bonus_value = 8
	denied_type = /obj/item/crusher_trophy/ice_wing

/obj/item/crusher_trophy/ice_wing/effect_desc()
	return "waveform collapse to prevent certain creatures from using certain attacks for <b>[bonus_value*0.1]</b> second\s"

/obj/item/crusher_trophy/ice_wing/on_mark_detonation(mob/living/target, mob/living/user)
	if(ishostile(target))
		var/mob/living/simple_animal/hostile/H = target
		if(H.ranged) //briefly delay ranged attacks
			if(H.ranged_cooldown >= world.time)
				H.ranged_cooldown += bonus_value
			else
				H.ranged_cooldown = bonus_value + world.time

//forgotten watcher
/obj/item/crusher_trophy/watcher_wing_forgotten
	name = "forgotten watcher wing"
	desc = "A wing with a terminal infection of the strange crystals."
	icon_state = "watcher_wing_crystal"
	denied_type = /obj/item/crusher_trophy/watcher_wing_forgotten
	gender = NEUTER
	bonus_value = 20
	var/deadly_shot = FALSE

/obj/item/crusher_trophy/watcher_wing_forgotten/effect_desc()
	return "waveform collapse to make the next magnetic pulse deal <b>[bonus_value]</b> damage"

/obj/item/crusher_trophy/watcher_wing_forgotten/examine(mob/user)
	. = ..()
	. += "<span class='notice'>Suitable as a trophy for a proto-kinetic crusher.</span>"

/obj/item/crusher_trophy/watcher_wing_forgotten/on_projectile_fire(obj/projectile/destabilizer/marker, mob/living/user)
	if(deadly_shot)
		marker.name = "crystal [marker.name]"
		marker.icon_state = "crystal_shard"
		marker.damage = bonus_value
		marker.nodamage = FALSE
		marker.speed = 2
		deadly_shot = FALSE

/obj/item/crusher_trophy/watcher_wing_forgotten/on_mark_detonation(mob/living/target, mob/living/user)
	deadly_shot = TRUE
	addtimer(CALLBACK(src, PROC_REF(reset_deadly_shot)), 300, TIMER_UNIQUE|TIMER_OVERRIDE)

/obj/item/crusher_trophy/watcher_wing_forgotten/proc/reset_deadly_shot()
	deadly_shot = FALSE

//legion
/obj/item/crusher_trophy/legion_skull
	name = "legion skull"
	desc = "A dead and lifeless legion skull. Could be used in crafting."
	icon_state = "legion_skull"
	denied_type = /obj/item/crusher_trophy/legion_skull
	bonus_value = 3

/obj/item/crusher_trophy/legion_skull/examine(mob/user)
	. = ..()
	. += "<span class='notice'>Suitable as a trophy for a proto-kinetic crusher.</span>"

/obj/item/crusher_trophy/legion_skull/effect_desc()
	return "a kinetic crusher to recharge <b>[bonus_value*0.1]</b> second\s faster"

/obj/item/crusher_trophy/legion_skull/add_to(obj/item/kinetic_crusher/H, mob/living/user)
	. = ..()
	if(.)
		H.charge_time -= bonus_value

/obj/item/crusher_trophy/legion_skull/remove_from(obj/item/kinetic_crusher/H, mob/living/user)
	. = ..()
	if(.)
		H.charge_time += bonus_value

//dwarf legion
/obj/item/crusher_trophy/dwarf_skull
	name = "shrunken skull"
	desc = "Looks like someone hasn't been drinking their milk. Could be used in crafting."
	icon = 'icons/obj/lavaland/elite_trophies.dmi'
	icon_state = "shrunk_skull"
	denied_type = /obj/item/crusher_trophy/dwarf_skull
	bonus_value = 6

/obj/item/crusher_trophy/dwarf_skull/effect_desc()
	return "a kinetic crusher to recharge <b>[bonus_value*0.1]</b> second\s faster"

/obj/item/crusher_trophy/dwarf_skull/add_to(obj/item/kinetic_crusher/H, mob/living/user)
	. = ..()
	if(.)
		H.charge_time -= bonus_value

/obj/item/crusher_trophy/dwarf_skull/remove_from(obj/item/kinetic_crusher/H, mob/living/user)
	. = ..()
	if(.)
		H.charge_time += bonus_value


//disfigured legion
/obj/item/crusher_trophy/legion_skull_crystal
	name = "disfigured legion skull"
	desc = "A dead and lifeless legion skull. The crystals keep it alive, even in agony."
	icon_state = "legion_skull_crystal"
	denied_type = /obj/item/crusher_trophy/legion_skull_crystal
	bonus_value = 1

/obj/item/crusher_trophy/legion_skull_crystal/examine(mob/user)
	. = ..()
	. += "<span class='notice'>Suitable as a trophy for a proto-kinetic crusher.</span>"

/obj/item/crusher_trophy/legion_skull_crystal/effect_desc()
	return "waveform collapse to shoot 3 projectiles that only hits hostile fauna"

/obj/item/crusher_trophy/legion_skull_crystal/on_mark_detonation(mob/living/target, mob/living/user)
	for(var/i in 0 to 5)
		var/obj/projectile/projectile_to_shoot = new /obj/projectile/crystalline_crusher(get_turf(src))
		projectile_to_shoot.preparePixelProjectile(get_step(src, pick(GLOB.alldirs)), get_turf(src))
		projectile_to_shoot.firer = user
		projectile_to_shoot.fire(i*(360/5))
	return ..()

/obj/projectile/crystalline_crusher
	name = "Crystalline Shard"
	icon_state = "crystal_shard"
	damage = 25
	damage_type = BRUTE
	speed = 3

/obj/projectile/crystalline_crusher/on_hit(atom/target, blocked)
	. = ..()
	var/turf/turf_hit = get_turf(target)
	new /obj/effect/temp_visual/goliath_tentacle/crystal/visual_only(turf_hit,firer)

/obj/projectile/crystalline_crusher/can_hit_target(atom/target, list/passthrough, direct_target, ignore_loc)
	if(!(istype(target,/mob/living/simple_animal/hostile/asteroid)))
		if(isturf(target))
			return ..()
		return FALSE
	return ..()

//blood-drunk hunter
/obj/item/crusher_trophy/miner_eye
	name = "eye of a blood-drunk hunter"
	desc = "Its pupil is collapsed and turned to mush."
	icon_state = "hunter_eye"
	denied_type = /obj/item/crusher_trophy/miner_eye

/obj/item/crusher_trophy/miner_eye/examine(mob/user)
	. = ..()
	. += "<span class='notice'>Suitable as a trophy for a proto-kinetic crusher.</span>"

/obj/item/crusher_trophy/miner_eye/effect_desc()
	return "waveform collapse to grant stun immunity and <b>90%</b> damage reduction for <b>1</b> second"

/obj/item/crusher_trophy/miner_eye/on_mark_detonation(mob/living/target, mob/living/user)
	user.apply_status_effect(STATUS_EFFECT_BLOODDRUNK)

//whelp
/obj/item/crusher_trophy/tail_spike
	desc = "A spike taken from a young dragon's tail. Sharp enough to stab someone with."
	denied_type = /obj/item/crusher_trophy/tail_spike
	bonus_value = 5
	force = 10
	throwforce = 15
	throw_speed = 4
	sharpness = IS_SHARP
	attack_verb = list("cut", "sliced", "diced")
	hitsound = 'sound/weapons/bladeslice.ogg'

/obj/item/crusher_trophy/tail_spike/effect_desc()
	return "waveform collapse to do <b>[bonus_value]</b> damage to nearby creatures and push them back"

/obj/item/crusher_trophy/tail_spike/on_mark_detonation(mob/living/target, mob/living/user)
	for(var/mob/living/L in oview(2, user))
		if(L.stat == DEAD)
			continue
		playsound(L, 'sound/magic/fireball.ogg', 20, TRUE)
		new /obj/effect/temp_visual/fire(L.loc)
		addtimer(CALLBACK(src, PROC_REF(pushback), L, user), 1) //no free backstabs, we push AFTER module stuff is done
		L.adjustFireLoss(bonus_value, forced = TRUE)

/obj/item/crusher_trophy/tail_spike/proc/pushback(mob/living/target, mob/living/user)
	if(!QDELETED(target) && !QDELETED(user) && (!target.anchored || ismegafauna(target))) //megafauna will always be pushed
		step(target, get_dir(user, target))

//ash drake
/obj/item/crusher_trophy/ash_spike
	desc = "A molten spike taken from an ash drake's tail. Hot to the touch and extremely sharp."
	icon = 'icons/obj/lavaland/elite_trophies.dmi'
	icon_state = "ash_spike"
	denied_type = /obj/item/crusher_trophy/ash_spike
	bonus_value = 15
	force = 15
	throwforce = 20
	throw_speed = 4
	sharpness = IS_SHARP
	attack_verb = list("cut", "braised", "singed")
	hitsound = 'sound/weapons/bladeslice.ogg'

/obj/item/crusher_trophy/ash_spike/effect_desc()
	return "waveform collapse to do <b>[bonus_value]</b> damage to nearby creatures and push them back"

/obj/item/crusher_trophy/ash_spike/examine(mob/user)
	. = ..()
	. += "<span class='notice'>Suitable as a trophy for a proto-kinetic crusher.</span>"

/obj/item/crusher_trophy/ash_spike/on_mark_detonation(mob/living/target, mob/living/user)
	for(var/mob/living/L in oview(2, user))
		if(L.stat == DEAD)
			continue
		playsound(L, 'sound/magic/fireball.ogg', 20, TRUE)
		new /obj/effect/temp_visual/fire(L.loc)
		addtimer(CALLBACK(src, PROC_REF(pushback), L, user), 1) //no free backstabs, we push AFTER module stuff is done
		L.adjustFireLoss(bonus_value, forced = TRUE)

/obj/item/crusher_trophy/ash_spike/proc/pushback(mob/living/target, mob/living/user)
	if(!QDELETED(target) && !QDELETED(user) && (!target.anchored || ismegafauna(target))) //megafauna will always be pushed
		step(target, get_dir(user, target))

//bubblegum
/obj/item/crusher_trophy/demon_claws
	name = "demon claws"
	desc = "A set of blood-drenched claws from a massive demon's hand."
	icon_state = "demon_claws"
	gender = PLURAL
	denied_type = /obj/item/crusher_trophy/demon_claws
	bonus_value = 10
	var/static/list/damage_heal_order = list(BRUTE, BURN, OXY)

/obj/item/crusher_trophy/demon_claws/effect_desc()
	return "melee hits to do <b>[bonus_value * 0.2]</b> more damage and heal you for <b>[bonus_value * 0.1]</b>, with <b>5X</b> effect on waveform collapse"

/obj/item/crusher_trophy/demon_claws/add_to(obj/item/kinetic_crusher/H, mob/living/user)
	. = ..()
	if(.)
		H.force += bonus_value * 0.2
		H.detonation_damage += bonus_value * 0.8
		AddComponent(/datum/component/two_handed, force_wielded=(20 + bonus_value * 0.2))

/obj/item/crusher_trophy/demon_claws/remove_from(obj/item/kinetic_crusher/H, mob/living/user)
	. = ..()
	if(.)
		H.force -= bonus_value * 0.2
		H.detonation_damage -= bonus_value * 0.8
		AddComponent(/datum/component/two_handed, force_wielded=20)

/obj/item/crusher_trophy/demon_claws/on_melee_hit(mob/living/target, mob/living/user)
	user.heal_ordered_damage(bonus_value * 0.1, damage_heal_order)

/obj/item/crusher_trophy/demon_claws/on_mark_detonation(mob/living/target, mob/living/user)
	user.heal_ordered_damage(bonus_value * 0.4, damage_heal_order)

//colossus
/obj/item/crusher_trophy/blaster_tubes
	name = "blaster tubes"
	desc = "The blaster tubes from a colossus's arm."
	icon_state = "blaster_tubes"
	gender = PLURAL
	denied_type = /obj/item/crusher_trophy/blaster_tubes
	bonus_value = 15
	var/deadly_shot = FALSE

/obj/item/crusher_trophy/blaster_tubes/examine(mob/user)
	. = ..()
	. += "<span class='notice'>Suitable as a trophy for a proto-kinetic crusher.</span>"

/obj/item/crusher_trophy/blaster_tubes/effect_desc()
	return "waveform collapse to make the next magnetic pulse deal <b>[bonus_value]</b> damage but move slower"

/obj/item/crusher_trophy/blaster_tubes/on_projectile_fire(obj/projectile/destabilizer/marker, mob/living/user)
	if(deadly_shot)
		marker.name = "ominous [marker.name]"
		marker.icon_state = "chronobolt"
		marker.damage = bonus_value
		marker.nodamage = FALSE
		marker.speed = 2
		deadly_shot = FALSE

/obj/item/crusher_trophy/blaster_tubes/on_mark_detonation(mob/living/target, mob/living/user)
	deadly_shot = TRUE
	addtimer(CALLBACK(src, PROC_REF(reset_deadly_shot)), 300, TIMER_UNIQUE|TIMER_OVERRIDE)

/obj/item/crusher_trophy/blaster_tubes/proc/reset_deadly_shot()
	deadly_shot = FALSE

//hierophant
/obj/item/crusher_trophy/vortex_talisman
	name = "vortex talisman"
	desc = "A glowing trinket that was originally the Hierophant's beacon."
	icon_state = "vortex_talisman"
	denied_type = /obj/item/crusher_trophy/vortex_talisman

/obj/item/crusher_trophy/vortex_talisman/effect_desc()
	return "waveform collapse to create a barrier you can pass"

/obj/item/crusher_trophy/vortex_talisman/on_mark_detonation(mob/living/target, mob/living/user)
	var/turf/current_location = get_turf(user)
	var/area/current_area = current_location.loc
	if(current_area.area_flags & NOTELEPORT)
		to_chat(user, "[src] fizzles uselessly.")
		return
	var/turf/T = get_turf(user)
	new /obj/effect/temp_visual/hierophant/wall/crusher(T, user) //a wall only you can pass!
	var/turf/otherT = get_step(T, turn(user.dir, 90))
	if(otherT)
		new /obj/effect/temp_visual/hierophant/wall/crusher(otherT, user)
	otherT = get_step(T, turn(user.dir, -90))
	if(otherT)
		new /obj/effect/temp_visual/hierophant/wall/crusher(otherT, user)

/obj/effect/temp_visual/hierophant/wall/crusher
	duration = 75

//I am afraid of this code. It also does not function(in terms of doing damage to enemies) as of my last test.
/obj/item/crusher_trophy/king_goat
	name = "king goat hoof"
	desc = "A hoof from the king of all goats, it still glows with a fraction of its original power..."
	icon_state = "goat_hoof" //needs a better sprite but I cant sprite .
	denied_type = /obj/item/crusher_trophy/king_goat

/obj/item/crusher_trophy/king_goat/examine(mob/user)
	. = ..()
	. += "<span class='notice'>Suitable as a trophy for a proto-kinetic crusher.</span>"

/obj/item/crusher_trophy/king_goat/effect_desc()
	return "you also passively recharge pulses 5x as fast while this is equipped and do a decent amount of damage at the cost of dulling the blade"

/obj/item/crusher_trophy/king_goat/on_projectile_fire(obj/projectile/destabilizer/marker, mob/living/user)
	marker.damage = 10 //in my testing only does damage to simple mobs so should be fine to have it high //it does damage to nobody. Please fix -M

/obj/item/crusher_trophy/king_goat/add_to(obj/item/kinetic_crusher/H, mob/living/user)
	. = ..()
	if(.)
		H.charge_time = 3
		H.AddComponent(/datum/component/two_handed, force_wielded=5)

/obj/item/crusher_trophy/king_goat/remove_from(obj/item/kinetic_crusher/H, mob/living/user)
	. = ..()
	if(.)
		H.charge_time = 15
		H.AddComponent(/datum/component/two_handed, force_wielded=20)

/obj/item/crusher_trophy/shiny
	name = "shiny nugget"
	icon = 'icons/obj/lavaland/elite_trophies.dmi'
	desc = "A glimmering nugget of dull metal. As it turns out, the fools were right- pyrite is a far rarer substance than gold in the space age. You could probably sell this for a fair price."
	icon_state = "nugget"
	gender = PLURAL
	denied_type = /obj/item/crusher_trophy/shiny

/obj/item/crusher_trophy/shiny/effect_desc()
	return "empowered butchering chances"

/obj/item/crusher_trophy/shiny/add_to(obj/item/kinetic_crusher/H, mob/living/user)
	. = ..()
	if(.)
		H.AddComponent(/datum/component/butchering, 60, 210)

/obj/item/crusher_trophy/shiny/remove_from(obj/item/kinetic_crusher/H, mob/living/user)
	. = ..()
	if(.)
		H.AddComponent(/datum/component/butchering, 60, 110)

/obj/item/crusher_trophy/lobster_claw
	name = "lobster claw"
	icon_state = "lobster_claw"
	desc = "A lobster claw."
	denied_type = /obj/item/crusher_trophy/lobster_claw
	bonus_value = 1

/obj/item/crusher_trophy/lobster_claw/effect_desc()
	return "mark detonation to briefly stagger the target for [bonus_value] seconds"

/obj/item/crusher_trophy/lobster_claw/on_mark_detonation(mob/living/target, mob/living/user)
	target.apply_status_effect(/datum/status_effect/stagger, bonus_value SECONDS)
