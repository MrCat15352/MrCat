/obj/machinery/computer/bounty_hunter
	name = "bounty hunter console"
	desc = "Консоль для создания и просмотра заявок на розыск. Позволяет назначить награду за поимку или устранение целей."
	icon_screen = "bounty"
	light_color = COLOR_BRIGHT_ORANGE
	circuit = /obj/item/circuitboard/computer/bounty_hunter
	
	/// Вставленная ID карта
	var/obj/item/card/id/inserted_id
	/// Режим консоли: "view" или "create"
	var/console_mode = "view"

/obj/machinery/computer/bounty_hunter/attackby(obj/item/W, mob/user, params)
	if(istype(W, /obj/item/card/id))
		if(inserted_id)
			to_chat(user, span_warning("В консоли уже есть ID карта!"))
			return
		if(!user.transferItemToLoc(W, src))
			return
		inserted_id = W
		to_chat(user, span_notice("Вы вставляете [W] в консоль."))
		update_appearance()
		return TRUE
	return ..()

/obj/machinery/computer/bounty_hunter/ui_interact(mob/user, datum/tgui/ui)
	ui = SStgui.try_update_ui(user, src, ui)
	if(!ui)
		ui = new(user, src, "BountyHunter", name)
		ui.open()

/obj/machinery/computer/bounty_hunter/ui_data(mob/user)
	var/list/data = list()
	
	data["mode"] = console_mode
	data["hasCard"] = !!inserted_id
	data["cardName"] = inserted_id?.registered_name || null
	data["cardFaction"] = null
	
	if(inserted_id)
		// Получаем фракцию из ship_access
		if(length(inserted_id.ship_access))
			var/datum/overmap/ship/controlled/ship = inserted_id.ship_access[1]
			if(ship?.source_template?.faction)
				data["cardFaction"] = ship.source_template.faction.name
	
	// Список всех bounty заявок
	data["bountyEntries"] = list()
	for(var/datum/bounty_hunter_entry/entry in get_bounty_entries())
		data["bountyEntries"] += list(list(
			"id" = entry.entry_id,
			"targetName" = entry.target_name,
			"targetFaction" = entry.target_faction,
			"status" = entry.target_status,
			"reason" = entry.reason,
			"reward" = entry.reward_amount,
			"clientName" = entry.client_name,
			"clientFaction" = entry.client_faction,
			"timeAgo" = time2text(entry.creation_time, "hh:mm DD/MM")
		))
	
	return data

/obj/machinery/computer/bounty_hunter/ui_act(action, list/params, datum/tgui/ui, datum/ui_state/state)
	. = ..()
	if(.)
		return
	
	switch(action)
		if("ejectCard")
			if(inserted_id)
				inserted_id.forceMove(drop_location())
				inserted_id = null
				update_appearance()
			return TRUE
			
		if("setMode")
			var/new_mode = params["mode"]
			if(new_mode in list("view", "create"))
				console_mode = new_mode
			return TRUE
			
		if("createBounty")
			if(!inserted_id)
				return FALSE
				
			var/target_name = params["targetName"]
			var/target_faction = params["targetFaction"] 
			var/target_status = params["targetStatus"]
			var/reason = params["reason"]
			var/reward = text2num(params["reward"])
			
			if(!target_name || !reason || !reward || reward <= 0)
				return FALSE
			
			// Получаем корабль для списания денег
			var/datum/overmap/ship/controlled/client_ship
			if(length(inserted_id.ship_access))
				client_ship = inserted_id.ship_access[1]
			
			if(!client_ship || !client_ship.ship_account)
				return FALSE
			
			// Проверяем баланс
			if(client_ship.ship_account.account_balance < reward)
				return FALSE
			
			// Списываем деньги
			if(!client_ship.ship_account.adjust_money(-reward))
				return FALSE
			
			// Получаем данные заказчика
			var/client_name = inserted_id.registered_name
			var/client_faction = ""
			if(client_ship?.source_template?.faction)
				client_faction = client_ship.source_template.faction.name
			
			// Создаем заявку
			var/datum/bounty_hunter_entry/new_entry = new(
				target_name,
				target_faction,
				target_status,
				reason,
				reward,
				client_name,
				client_faction,
				inserted_id
			)
			
			add_bounty_entry(new_entry)
			console_mode = "view"
			return TRUE
			
		if("removeBounty")
			var/entry_id = params["entryId"]
			if(!entry_id || !inserted_id)
				return FALSE
				
			// Проверяем, что заявку удаляет её создатель
			for(var/datum/bounty_hunter_entry/entry in get_bounty_entries())
				if(entry.entry_id == entry_id && entry.client_id == inserted_id)
					// Возвращаем деньги на корабельный счёт
					var/datum/overmap/ship/controlled/refund_ship
					if(length(inserted_id.ship_access))
						refund_ship = inserted_id.ship_access[1]
					if(refund_ship && refund_ship.ship_account)
						refund_ship.ship_account.adjust_money(entry.reward_amount)
					remove_bounty_entry(entry_id)
					return TRUE
			return FALSE

/obj/item/circuitboard/computer/bounty_hunter
	name = "Bounty Hunter Console"
	build_path = /obj/machinery/computer/bounty_hunter