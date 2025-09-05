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
	var/scribble = ""
	var/scribble_page = null
	var/wantedAuthor
	var/wantedCriminal
	var/wantedBody
	var/wantedPhoto
	var/creationTime
	var/list/random_articles = list() // Сгенерированные случайные статьи
	var/issue_number // Номер выпуска

/obj/item/newspaper/Initialize(mapload)
	. = ..()
	creationTime = GLOB.news_network.last_action
	issue_number = rand(1000, 9999) // Статичный номер выпуска
	
	for(var/datum/feed_channel/iterated_feed_channel in GLOB.news_network.network_channels)
		news_content += iterated_feed_channel

	// Проверяем активные розыски
	for(var/datum/wanted_message/wanted in GLOB.news_network.wanted_issues)
		if(wanted.active)
			wantedAuthor = wanted.scanned_user
			wantedCriminal = wanted.criminal
			wantedBody = wanted.body
			if(wanted.img)
				wantedPhoto = wanted.img
			break // Берем первый активный розыск
	
	// Fallback на старую систему
	if(!wantedCriminal && GLOB.news_network.wanted_issue.active)
		wantedAuthor = GLOB.news_network.wanted_issue.scanned_user
		wantedCriminal = GLOB.news_network.wanted_issue.criminal
		wantedBody = GLOB.news_network.wanted_issue.body
		if(GLOB.news_network.wanted_issue.img)
			wantedPhoto = GLOB.news_network.wanted_issue.img
	
	// Случайные новости теперь создаются в newscaster

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
	data["wanted_criminal"] = wantedCriminal
	data["wanted_body"] = wantedBody
	data["wanted_photo"] = wantedPhoto
	data["issue_number"] = issue_number
	
	// Подсчитываем страницы
	pages = news_content.len
	data["pages"] = pages
	
	// Список каналов
	var/list/channels_list = list()
	for(var/datum/feed_channel/channel in news_content)
		var/message_count = 0
		for(var/datum/feed_message/message in channel.messages)
			if(message.creation_time <= creationTime)
				message_count++
		channels_list += list(list(
			"name" = channel.channel_name,
			"author" = channel.author,
			"messages" = message_count
		))
	data["channels"] = channels_list
	
	// Данные текущего канала
	var/list/channel_data = list()
	if(curr_page > 0 && curr_page <= pages)
		var/list/messages_list = list()
		
		// Получаем данные канала
		if(curr_page <= news_content.len)
			var/datum/feed_channel/current_channel = news_content[curr_page]
			if(current_channel)
				channel_data["name"] = current_channel.channel_name
				channel_data["author"] = current_channel.author
				channel_data["censored"] = current_channel.censored
				
				// Сообщения канала
				for(var/datum/feed_message/message in current_channel.messages)
					// Фильтруем по времени создания
					if(message.creation_time <= creationTime)
						messages_list += list(list(
							"body" = message.return_body(-1),
							"author" = message.return_author(-1),
							"time" = message.time_stamp,
							"img" = message.img
						))
		
		channel_data["messages"] = messages_list
	data["channel_data"] = channel_data
	
	return data

/obj/item/newspaper/ui_act(action, params)
	. = ..()
	if(.)
		return
	
	switch(action)
		if("next_page")
			// Максимальная страница: каналы + розыск (если есть)
			var/max_page = pages
			if(wantedCriminal)
				max_page++
			if(curr_page < max_page)
				curr_page++
				playsound(loc, "pageturn", 50, TRUE)
				. = TRUE
		if("prev_page")
			if(curr_page > 0)
				curr_page--
				playsound(loc, "pageturn", 50, TRUE)
				. = TRUE

/obj/item/newspaper/attackby(obj/item/W, mob/living/user, params)
	if(istype(W, /obj/item/pen))
		if(!user.is_literate())
			to_chat(user, span_notice("Ты пишешь неразборчиво на [src]!"))
			return
		if(scribble_page == curr_page)
			to_chat(user, span_warning("На этой странице уже есть заметка... Не стоит делать все слишком загроможденным, не так ли?"))
		else
			var/s = stripped_input(user, "Напишите что-нибудь", "Газета")
			if (!s)
				return
			if(!user.canUseTopic(src, BE_CLOSE))
				return
			scribble_page = curr_page
			scribble = s
			to_chat(user, span_notice("Вы написали заметку на странице [curr_page + 1]."))
			add_fingerprint(user)
	else
		return ..()

// Система генерации случайных новостей
/obj/item/newspaper/proc/generate_random_content()
	var/list/news_templates = list(
		// Обычные новости
		list(
			"title" = "Новости смены",
			"body" = "Сегодня на станции было относительно спокойно. Отдел инженерии сообщает о стабильной работе всех систем.",
			"author" = "Корреспондент Грифона"
		),
		list(
			"title" = "Медицинские новости",
			"body" = "Медбай напоминает всем сотрудникам о необходимости прохождения плановых медосмотров. Помните: здоровье - это ваше богатство!",
			"author" = "Главврач станции"
		),
		list(
			"title" = "Отдел снабжения",
			"body" = "На складе появились новые поставки оборудования. Квартирмейстер просит всех ответственно относиться к имуществу компании.",
			"author" = "Отдел снабжения"
		),
		// Интересные события
		list(
			"title" = "Необычные происшествия",
			"body" = "В отделе исследований замечены необычные флуктуации в работе оборудования. Ученые продолжают изучение явления.",
			"author" = "Научный отдел"
		),
		list(
			"title" = "Кулинарные новости",
			"body" = "Повар станции представил новое блюдо в меню кафетерия. По словам персонала, это настоящий кулинарный шедевр!",
			"author" = "Кулинарный обозреватель"
		),
		// Объявления
		list(
			"title" = "Объявления",
			"body" = "Напоминаем всем сотрудникам о необходимости соблюдения правил безопасности. Помните: безопасность - превыше всего!",
			"author" = "Администрация"
		),
		// Развлекательные
		list(
			"title" = "Спортивные новости",
			"body" = "В рекреационной зоне состоялся турнир по настольному теннису. Победитель получил почетный кубок и дополнительные выходные.",
			"author" = "Спортобозреватель"
		),
		list(
			"title" = "Космическая погода",
			"body" = "Метеорологическая служба сообщает о спокойной космической погоде. Магнитные бури не прогнозируются. Отличные условия для работы!",
			"author" = "Метеослужба"
		),
		list(
			"title" = "Корпоративные новости",
			"body" = "Nanotrasen объявляет о новой программе мотивации сотрудников. Лучшие работники месяца получат ценные призы и повышение зарплаты.",
			"author" = "HR-отдел"
		),
		list(
			"title" = "Технические новости",
			"body" = "Инженерный отдел завершил модернизацию системы вентиляции. Теперь воздух на станции стал еще чище и свежее. Дышите полной грудью!",
			"author" = "Главный инженер"
		),
		list(
			"title" = "Культурная жизнь",
			"body" = "В библиотеке открылась выставка редких книг. Посетители могут ознакомиться с уникальными изданиями по истории космонавтики.",
			"author" = "Библиотекарь"
		),
		// Смешные/необычные
		list(
			"title" = "Потерянные вещи",
			"body" = "В бюро находок поступило необычное количество потерянных носков. Просим владельцев обращаться за получением. Мы не кусаемся!",
			"author" = "Охрана"
		),
		list(
			"title" = "Мистические явления",
			"body" = "Несколько сотрудников сообщили о странных звуках в вентиляционных шахтах. Инженеры утверждают, что это обычные технические шумы. Но мы не уверены...",
			"author" = "Неизвестный автор"
		)
	)
	
	// Всегда генерируем 3-5 случайных статей
	var/articles_to_generate = 4
	for(var/i = 1 to articles_to_generate)
		if(news_templates.len > 0)
			var/list/template = pick(news_templates)
			news_templates -= template
			random_articles += template
			
	// Добавляем рекламные объявления
	var/list/ads = list(
		"Кафетерий 'У Мамы' - лучшая еда на станции!",
		"Магазин 'Robust Tools' - инструменты для настоящих профессионалов!",
		"Медбай напоминает: здоровье - это ваше богатство!"
	)
	if(ads.len > 0)
		random_articles += list(list(
			"title" = "Рекламные объявления",
			"body" = pick(ads),
			"author" = "Рекламный отдел"
		))