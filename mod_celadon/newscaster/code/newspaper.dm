/obj/item/newspaper
	name = "newspaper"
	desc = "Выпуск газеты «Griffon», часто распространяемой на борту космических станций «Nanotrasen»."
	icon = 'icons/obj/bureaucracy.dmi'
	icon_state = "newspaper"
	lefthand_file = 'icons/mob/inhands/misc/books_lefthand.dmi'
	righthand_file = 'icons/mob/inhands/misc/books_righthand.dmi'
	w_class = WEIGHT_CLASS_SMALL
	attack_verb = list("bapped")
	resistance_flags = FLAMMABLE
	var/screen = 0
	var/pages = 0
	var/curr_page = 0
	var/list/datum/feed_channel/news_content = list()
	var/scribble=""
	var/scribble_page = null
	var/wantedAuthor
	var/wantedCriminal
	var/wantedBody
	var/wantedPhoto
	var/creationTime

/obj/item/newspaper/Initialize(mapload)
	. = ..()
	creationTime = GLOB.news_network.last_action
	for(var/datum/feed_channel/iterated_feed_channel in GLOB.news_network.network_channels)
		news_content += iterated_feed_channel

	if(!GLOB.news_network.wanted_issue.active)
		return
	wantedAuthor = GLOB.news_network.wanted_issue.scanned_user
	wantedCriminal = GLOB.news_network.wanted_issue.criminal
	wantedBody = GLOB.news_network.wanted_issue.body
	if(GLOB.news_network.wanted_issue.img)
		wantedPhoto = GLOB.news_network.wanted_issue.img

/obj/item/newspaper/attack_self(mob/user)
	ui_interact(user)

/obj/item/newspaper/ui_interact(mob/user, datum/tgui/ui)
	ui = SStgui.try_update_ui(user, src, ui)
	if(!ui)
		ui = new(user, src, "Newspaper")
		ui.open()

/obj/item/newspaper/ui_data(mob/user)
	var/list/data = list()
	data["current_page"] = curr_page
	data["scribble_message"] = scribble
	data["channel_has_messages"] = FALSE
	data["channels"] = list()
	data["channel_data"] = list()
	data["wanted_criminal"] = wantedCriminal
	data["wanted_body"] = wantedBody
	data["wanted_photo"] = wantedPhoto
	return data

/obj/item/newspaper/ui_act(action, params)
	. = ..()
	if(.)
		return
	
	switch(action)
		if("next_page")
			if(curr_page < pages)
				curr_page++
				. = TRUE
		if("prev_page")
			if(curr_page > 0)
				curr_page--
				. = TRUE

/obj/item/newspaper/attackby(obj/item/W, mob/living/user, params)
	if(burn_paper_product_attackby_check(W, user))
		return

	if(istype(W, /obj/item/pen))
		if(!user.is_literate())
			to_chat(user, span_notice("Ты пишешь неразборчиво [src]!"))
			return
		if(scribble_page == curr_page)
			to_chat(user, span_warning("На этой странице уже есть каракули... Вы же не хотите, чтобы все было слишком непонятно, не так ли?"))
		else
			var/s = stripped_input(user, "Write something", "Newspaper")
			if (!s)
				return
			if(!user.canUseTopic(src, BE_CLOSE))
				return
			scribble_page = curr_page
			scribble = s
			attack_self(user)
			add_fingerprint(user)
	else
		return ..()