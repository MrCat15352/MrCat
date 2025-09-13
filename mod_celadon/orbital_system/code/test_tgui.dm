//Test TGUI interface

/datum/test_tgui

/datum/test_tgui/ui_interact(mob/user, datum/tgui/ui)
	ui = SStgui.try_update_ui(user, src, ui)
	if(!ui)
		ui = new(user, src, "TestLocalMap", "Test Interface")
		ui.open()

/datum/test_tgui/ui_data(mob/user)
	return list("test" = "data")

/datum/test_tgui/ui_act(action, list/params, datum/tgui/ui, datum/ui_state/state)
	if(action == "test_action")
		to_chat(usr, "Test action worked!")
		return TRUE
	return FALSE