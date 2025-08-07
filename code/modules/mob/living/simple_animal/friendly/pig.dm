//PIG SYSTEM WITH FEEDING AND MUTATIONS
/mob/living/simple_animal/pig
	name = "pig"
	desc = "A fat, lazy pig. Oink oink!"
	icon_state = "pig"
	icon_living = "pig"
	icon_dead = "pig_dead"
	gender = NEUTER
	mob_biotypes = MOB_ORGANIC|MOB_BEAST
	speak = list("oink", "oink oink", "snort")
	speak_emote = list("oinks", "snorts")
	emote_hear = list("oinks.", "snorts.")
	emote_see = list("rolls around.", "snorts loudly.")
	speak_chance = 2
	turns_per_move = 8
	see_in_dark = 6
	butcher_results = list(/obj/item/food/meat/slab = 4)
	response_help_continuous = "pets"
	response_help_simple = "pet"
	response_disarm_continuous = "gently pushes aside"
	response_disarm_simple = "gently push aside"
	response_harm_continuous = "kicks"
	response_harm_simple = "kick"
	attack_verb_continuous = "bites"
	attack_verb_simple = "bite"
	health = 60
	maxHealth = 60
	blood_volume = BLOOD_VOLUME_NORMAL
	footstep_type = FOOTSTEP_MOB_SHOE
	
	// Pig-specific vars
	var/fullness = 0
	var/max_fullness = 100
	var/size_multiplier = 1.0
	var/oink_frequency = 2
	var/last_oink = 0
	var/mutation_type = "normal"
	var/dirt_timer = 0
	var/list/mutation_foods = list()

/mob/living/simple_animal/pig/Initialize()
	. = ..()
	mutation_foods = list(
		/obj/item/food/grown/cannabis = "rainbow",
		/obj/item/book/bible = "holy", 
		/obj/item/stack/sheet/iron = "cyborg",
		/obj/item/food/badrecipe = "fat"
	)

/mob/living/simple_animal/pig/attackby(obj/item/O, mob/user, params)
	if(istype(O, /obj/item/food) || istype(O, /obj/item/book/bible) || istype(O, /obj/item/stack/sheet/iron))
		feed_pig(O, user)
		return
	return ..()

/mob/living/simple_animal/pig/proc/feed_pig(obj/item/food_item, mob/user)
	if(fullness >= max_fullness)
		to_chat(user, span_warning("[src] is too full to eat more!"))
		return
		
	user.visible_message(span_notice("[user] feeds [food_item] to [src]."))
	
	// Check for mutations
	for(var/food_type in mutation_foods)
		if(istype(food_item, food_type))
			mutate_pig(mutation_foods[food_type])
			break
	
	// Increase fullness
	if(istype(food_item, /obj/item/food/badrecipe))
		fullness += 15
		grow_pig()
	else
		fullness += 5
	
	qdel(food_item)
	
	// Check for turbo pig transformation
	if(fullness >= max_fullness)
		become_turbo_pig()

/mob/living/simple_animal/pig/proc/grow_pig()
	size_multiplier += 0.1
	transform = transform.Scale(1.05)
	butcher_results = list(/obj/item/food/meat/slab = round(4 * size_multiplier))
	
	if(size_multiplier > 1.5)
		oink_frequency = min(oink_frequency + 1, 10)
		
	visible_message(span_notice("[src] grows larger!"))

/mob/living/simple_animal/pig/proc/mutate_pig(mutation)
	if(mutation_type == mutation)
		return
		
	mutation_type = mutation
	
	switch(mutation)
		if("rainbow")
			name = "rainbow pig"
			desc = "A colorful pig that shimmers with rainbow colors!"
			color = rgb(rand(100,255), rand(100,255), rand(100,255))
			butcher_results = list(/obj/item/food/meat/slab/rainbow = 4)
			
		if("holy")
			name = "holy pig"
			desc = "A blessed pig that radiates divine energy."
			add_atom_colour("#FFD700", ADMIN_COLOUR_PRIORITY)
			butcher_results = list(/obj/item/food/meat/slab/holy = 4)
			
		if("cyborg")
			name = "cyborg pig"
			desc = "A mechanically enhanced pig with metal parts."
			add_atom_colour("#C0C0C0", ADMIN_COLOUR_PRIORITY)
			butcher_results = list(/obj/item/food/meat/slab/synthetic = 4)
			
	visible_message(span_boldnotice("[src] undergoes a strange transformation!"))

/mob/living/simple_animal/pig/proc/become_turbo_pig()
	var/mob/living/simple_animal/pig/turbo/T = new(loc)
	T.mutation_type = mutation_type
	T.color = color
	T.name = replacetext(name, "pig", "turbo pig")
	T.desc = "An overfed pig that moves with surprising speed and makes constant noise!"
	qdel(src)

/mob/living/simple_animal/pig/Life()
	. = ..()
	if(!.)
		return
		
	// Oink based on frequency
	if(world.time - last_oink > (60 / oink_frequency))
		if(prob(30))
			audible_message(span_notice("[src] oinks loudly!"))
			playsound(src, 'sound/creatures/pig_oink.ogg', 50, TRUE)
		last_oink = world.time
	
	// Slowly reduce fullness
	if(fullness > 0)
		fullness = max(0, fullness - 0.5)

// TURBO PIG - Overfed pig
/mob/living/simple_animal/pig/turbo
	name = "turbo pig"
	desc = "An overfed pig that's become hyperactive and messy!"
	icon_state = "pig_turbo"
	speak_chance = 20
	turns_per_move = 2
	health = 100
	maxHealth = 100
	var/dirt_chance = 15

/mob/living/simple_animal/pig/turbo/Initialize()
	. = ..()
	transform = transform.Scale(1.5)
	butcher_results = list(/obj/item/food/meat/slab = 8)

/mob/living/simple_animal/pig/turbo/Life()
	. = ..()
	if(!.)
		return
		
	// Oink twice per second
	if(prob(33))
		audible_message(span_warning("[src] OINKS LOUDLY!"))
		playsound(src, 'sound/creatures/pig_oink.ogg', 75, TRUE)
	
	// Create dirt
	if(prob(dirt_chance))
		var/turf/T = get_turf(src)
		if(T && !locate(/obj/effect/decal/cleanable/dirt) in T)
			new /obj/effect/decal/cleanable/dirt(T)

// SPECIAL MEAT TYPES
/obj/item/food/meat/slab/rainbow
	name = "rainbow meat"
	desc = "Meat that shimmers with all colors of the rainbow."
	icon_state = "meat_rainbow"
	
/obj/item/food/meat/slab/rainbow/Initialize()
	. = ..()
	color = rgb(rand(100,255), rand(100,255), rand(100,255))

/obj/item/food/meat/slab/holy
	name = "blessed meat"
	desc = "Meat blessed by divine power. Eating it might heal you."
	icon_state = "meat_holy"
	
/obj/item/food/meat/slab/holy/attack(mob/living/M, mob/user)
	. = ..()
	if(ishuman(M))
		M.heal_overall_damage(10, 10)
		to_chat(M, span_notice("You feel blessed!"))

/obj/item/food/meat/slab/synthetic
	name = "synthetic meat"
	desc = "Meat with metallic components. Might be useful for repairs."
	icon_state = "meat_synthetic"
	
/obj/item/food/meat/slab/synthetic/attack(mob/living/M, mob/user)
	. = ..()
	if(iscyborg(M))
		M.heal_overall_damage(15, 15)
		to_chat(M, span_notice("Your systems feel optimized!"))