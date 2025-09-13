//Simple test for TGUI

/client/verb/simple_tgui_test()
	set name = "Simple TGUI Test"
	set category = "Debug"
	
	var/datum/simple_test/test = new()
	test.ui_interact(usr)

/datum/simple_test

/datum/simple_test/ui_interact(mob/user, datum/tgui/ui)
	ui = SStgui.try_update_ui(user, src, ui)
	if(!ui)
		ui = new(user, src, "TestLocalMap")
		ui.open()

/datum/simple_test/ui_data(mob/user)
	return list("message" = "Hello World!")

/datum/simple_test/ui_act(action, list/params, datum/tgui/ui, datum/ui_state/state)
	to_chat(usr, "Action received: [action]")
	return TRUE