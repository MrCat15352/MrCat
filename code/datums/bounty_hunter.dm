/datum/bounty_hunter_entry
	/// Имя цели
	var/target_name
	/// Фракция цели
	var/target_faction
	/// Статус: "Живым" или "Мёртвым"
	var/target_status = "Живым или мёртвым"
	/// Причина bounty
	var/reason
	/// Цена за голову
	var/reward_amount = 0
	/// Имя заказчика
	var/client_name
	/// Фракция заказчика
	var/client_faction
	/// ID карта заказчика (для проверки)
	var/obj/item/card/id/client_id
	/// Время создания заявки
	var/creation_time
	/// Уникальный ID заявки
	var/entry_id

/datum/bounty_hunter_entry/New(target, t_faction, status, reason_text, reward, client, c_faction, id_card)
	target_name = target
	target_faction = t_faction
	target_status = status
	reason = reason_text
	reward_amount = reward
	client_name = client
	client_faction = c_faction
	client_id = id_card
	creation_time = world.time
	entry_id = "[world.time]-[rand(1000,9999)]"

GLOBAL_LIST_EMPTY(bounty_hunter_entries)

/proc/add_bounty_entry(datum/bounty_hunter_entry/entry)
	if(!entry)
		return FALSE
	GLOB.bounty_hunter_entries += entry
	// Уведомление всех консолей о новой заявке
	for(var/obj/machinery/computer/bounty_hunter/console in GLOB.machines)
		if(console.machine_stat & (NOPOWER|BROKEN))
			continue
		playsound(console, 'sound/machines/twobeep_high.ogg', 30, TRUE)
	return TRUE

/proc/remove_bounty_entry(entry_id)
	for(var/datum/bounty_hunter_entry/entry in GLOB.bounty_hunter_entries)
		if(entry.entry_id == entry_id)
			GLOB.bounty_hunter_entries -= entry
			qdel(entry)
			return TRUE
	return FALSE

/proc/get_bounty_entries()
	return GLOB.bounty_hunter_entries