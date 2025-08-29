GLOBAL_DATUM_INIT(news_network, /datum/feed_network, new)
GLOBAL_LIST_EMPTY(allCasters)

/datum/feed_comment
	var/author = ""
	var/body = ""
	var/time_stamp = ""

/datum/feed_message
	var/author =""
	var/body =""
	var/list/author_censor_time = list()
	var/list/body_censor_time = list()
	var/is_admin_message = FALSE
	var/icon/img = null
	var/time_stamp = ""
	var/list/datum/feed_comment/comments = list()
	var/locked = FALSE
	var/caption = ""
	var/creation_time
	var/author_censor
	var/authorCensor = FALSE // Legacy compatibility
	var/body_censor
	var/bodyCensor = FALSE // Legacy compatibility
	var/photo_file
	var/parent_ID
	var/message_ID
	var/list/likes = list() // Список пользователей которые поставили лайк
	var/list/dislikes = list() // Список пользователей которые поставили дизлайк

/datum/feed_message/proc/return_author(censor)
	if(censor == -1)
		censor = author_censor
	var/txt = "[GLOB.news_network.redacted_text]"
	if(!censor)
		txt = author
	return txt

/datum/feed_message/proc/return_body(censor)
	if(censor == -1)
		censor = body_censor
	var/txt = "[GLOB.news_network.redacted_text]"
	if(!censor)
		txt = body
	return txt

// Legacy compatibility
/datum/feed_message/proc/returnBody(censor = -1)
	return return_body(censor)

/datum/feed_message/proc/returnAuthor(censor = -1)
	return return_author(censor)

/datum/feed_message/proc/toggle_censor_author()
	if(author_censor)
		author_censor_time.Add(GLOB.news_network.last_action*-1)
	else
		author_censor_time.Add(GLOB.news_network.last_action)
	author_censor = !author_censor
	GLOB.news_network.last_action ++

/datum/feed_message/proc/toggle_censor_body()
	if(body_censor)
		body_censor_time.Add(GLOB.news_network.last_action*-1)
	else
		body_censor_time.Add(GLOB.news_network.last_action)
	body_censor = !body_censor
	GLOB.news_network.last_action ++

// Legacy compatibility
/datum/feed_message/proc/toggleCensorAuthor()
	toggle_censor_author()

/datum/feed_message/proc/toggleCensorBody()
	toggle_censor_body()

/datum/feed_channel
	var/channel_name = ""
	var/channel_desc = ""
	var/list/datum/feed_message/messages = list()
	var/locked = FALSE
	var/author = ""
	var/censored = FALSE
	var/list/author_censor_time = list()
	var/list/D_class_censor_time = list()
	var/author_censor
	var/authorCensor = FALSE // Legacy compatibility
	var/is_admin_channel = FALSE
	var/channel_ID

/datum/feed_channel/New()
	. = ..()
	channel_ID = random_channel_id_setup()

/datum/feed_channel/proc/random_channel_id_setup()
	if(!GLOB.news_network)
		return
	if(!GLOB.news_network.channel_IDs)
		GLOB.news_network.channel_IDs += rand(1,999)
		return
	var/channel_id
	for(var/i in 1 to 10000)
		channel_id = rand(1, 999)
		if(!GLOB.news_network.channel_IDs["[channel_ID]"])
			break
	channel_ID = channel_id
	return channel_ID

/datum/feed_channel/proc/return_author(censor)
	if(censor == -1)
		censor = author_censor
	var/txt = "[GLOB.news_network.redacted_text]"
	if(!censor)
		txt = author
	return txt

// Legacy compatibility
/datum/feed_channel/proc/returnAuthor(censor = -1)
	return return_author(censor)

/datum/feed_channel/proc/toggle_censor_D_class()
	if(censored)
		D_class_censor_time.Add(GLOB.news_network.last_action*-1)
	else
		D_class_censor_time.Add(GLOB.news_network.last_action)
	censored = !censored
	GLOB.news_network.last_action ++

/datum/feed_channel/proc/toggle_censor_author()
	if(author_censor)
		author_censor_time.Add(GLOB.news_network.last_action*-1)
	else
		author_censor_time.Add(GLOB.news_network.last_action)
	author_censor = !author_censor
	GLOB.news_network.last_action ++

// Legacy compatibility
/datum/feed_channel/proc/toggleCensorAuthor()
	toggle_censor_author()

/datum/feed_channel/proc/toggleCensorDclass()
	toggle_censor_D_class()

/datum/wanted_message
	var/active
	var/criminal
	var/body
	var/scanned_user
	var/scannedUser // Legacy compatibility
	var/is_admin_msg
	var/icon/img
	var/photo_file
	var/wanted_ID // Unique ID for each wanted issue

/datum/feed_network
	var/list/datum/feed_channel/network_channels = list()
	var/datum/wanted_message/wanted_issue // Legacy compatibility
	var/list/datum/wanted_message/wanted_issues = list() // New multiple wanted system
	var/last_action
	var/redacted_text = "\[REDACTED\]"
	var/list/channel_IDs = list()
	var/message_count = 0
	var/wanted_count = 0

/datum/feed_network/New()
	create_feed_channel("Колониальная сеть объявлений", "SS13", "Новости компании, объявления персонала и вся актуальная информация. Удачной смены!", locked = TRUE, hardset_channel = 1000)
	wanted_issue = new /datum/wanted_message

/datum/feed_network/proc/create_feed_channel(channel_name, author, desc, locked, adminChannel = FALSE, hardset_channel)
	var/datum/feed_channel/newChannel = new /datum/feed_channel
	newChannel.channel_name = channel_name
	newChannel.author = author
	newChannel.channel_desc = desc
	newChannel.locked = locked
	newChannel.is_admin_channel = adminChannel
	if(hardset_channel)
		newChannel.channel_ID = hardset_channel
	network_channels += newChannel

/datum/feed_network/proc/submit_article(msg, author, channel_name, datum/picture/picture, adminMessage = FALSE, allow_comments = TRUE, update_alert = TRUE)
	var/datum/feed_message/newMsg = new /datum/feed_message
	newMsg.author = author
	newMsg.body = msg
	newMsg.time_stamp = "[station_time_timestamp()]"
	newMsg.is_admin_message = adminMessage
	newMsg.locked = !allow_comments
	if(picture)
		newMsg.img = picture.picture_image
		newMsg.caption = picture.caption
		newMsg.photo_file = save_photo(picture.picture_image)
	for(var/datum/feed_channel/FC in network_channels)
		if(FC.channel_name == channel_name)
			FC.messages += newMsg
			newMsg.parent_ID = FC.channel_ID
			break
	for(var/obj/machinery/newscaster/NEWSCASTER in GLOB.allCasters)
		NEWSCASTER.news_alert(channel_name, update_alert)
	last_action ++
	newMsg.creation_time = last_action
	message_count ++
	newMsg.message_ID = message_count

/datum/feed_network/proc/submit_wanted(criminal, body, scanned_user, datum/picture/picture, adminMsg = FALSE, newMessage = FALSE)
	// Legacy compatibility - update old wanted_issue
	wanted_issue.active = TRUE
	wanted_issue.criminal = criminal
	wanted_issue.body = body
	wanted_issue.scanned_user = scanned_user
	wanted_issue.scannedUser = scanned_user
	wanted_issue.is_admin_msg = adminMsg
	if(picture)
		wanted_issue.img = picture.picture_image
		wanted_issue.photo_file = save_photo(picture.picture_image)

	// New multiple wanted system
	var/datum/wanted_message/new_wanted = new /datum/wanted_message
	new_wanted.active = TRUE
	new_wanted.criminal = criminal
	new_wanted.body = body
	new_wanted.scanned_user = scanned_user
	new_wanted.scannedUser = scanned_user
	new_wanted.is_admin_msg = adminMsg
	new_wanted.wanted_ID = ++wanted_count
	if(picture)
		new_wanted.img = picture.picture_image
		new_wanted.photo_file = save_photo(picture.picture_image)
	wanted_issues += new_wanted

	if(newMessage)
		for(var/obj/machinery/newscaster/N in GLOB.allCasters)
			N.news_alert()
			N.update_appearance()
	return new_wanted.wanted_ID

/datum/feed_network/proc/delete_wanted()
	// Legacy - clear old wanted_issue
	wanted_issue.active = FALSE
	wanted_issue.criminal = null
	wanted_issue.body = null
	wanted_issue.scanned_user = null
	wanted_issue.scannedUser = null
	wanted_issue.img = null
	// Clear all wanted issues
	wanted_issues.Cut()
	for(var/obj/machinery/newscaster/updated_newscaster in GLOB.allCasters)
		updated_newscaster.update_appearance()

/datum/feed_network/proc/delete_wanted_by_id(wanted_id)
	for(var/datum/wanted_message/wanted in wanted_issues)
		if(wanted.wanted_ID == wanted_id)
			// Не удаляем, а помечаем как неактивный
			wanted.active = FALSE
			// Update legacy - проверяем есть ли активные розыски
			var/has_active = FALSE
			for(var/datum/wanted_message/check_wanted in wanted_issues)
				if(check_wanted.active)
					has_active = TRUE
					break
			if(!has_active)
				wanted_issue.active = FALSE
				wanted_issue.criminal = null
				wanted_issue.body = null
			for(var/obj/machinery/newscaster/updated_newscaster in GLOB.allCasters)
				updated_newscaster.update_appearance()
			return TRUE
	return FALSE

/datum/feed_network/proc/save_photo(icon/photo)
	var/photo_file = copytext_char(md5("\\icon[photo]"), 1, 6)
	if(!fexists("[GLOB.log_directory]/photos/[photo_file].png"))
		var/icon/clean = new /icon()
		clean.Insert(photo, "", SOUTH, 1, 0)
		fcopy(clean, "[GLOB.log_directory]/photos/[photo_file].png")
	return photo_file

// Legacy compatibility procs
/datum/feed_network/proc/CreateFeedChannel(channel_name, author, desc, locked, adminChannel = FALSE)
	return create_feed_channel(channel_name, author, desc, locked, adminChannel)

/datum/feed_network/proc/SubmitArticle(msg, author, channel_name, datum/picture/picture, adminMessage = FALSE, allow_comments = TRUE, update_alert = TRUE)
	return submit_article(msg, author, channel_name, picture, adminMessage, allow_comments, update_alert)

/datum/feed_network/proc/submitWanted(criminal, body, scanned_user, datum/picture/picture, adminMsg = FALSE, newMessage = FALSE)
	return submit_wanted(criminal, body, scanned_user, picture, adminMsg, newMessage)

/datum/feed_network/proc/deleteWanted()
	return delete_wanted()
