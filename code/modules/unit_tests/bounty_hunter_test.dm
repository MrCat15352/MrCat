/datum/unit_test/bounty_hunter_basic
	name = "Bounty Hunter System Basic Test"

/datum/unit_test/bounty_hunter_basic/Run()
	// Тест создания bounty entry
	var/datum/bounty_hunter_entry/test_entry = new(
		"Test Target",
		"Test Faction", 
		"Живым или мёртвым",
		"Test reason",
		1000,
		"Test Client",
		"Test Client Faction",
		null
	)
	
	TEST_ASSERT(test_entry.target_name == "Test Target", "Target name should be set correctly")
	TEST_ASSERT(test_entry.reward_amount == 1000, "Reward amount should be set correctly")
	TEST_ASSERT(test_entry.entry_id, "Entry ID should be generated")
	
	// Тест добавления в глобальный список
	add_bounty_entry(test_entry)
	TEST_ASSERT(test_entry in GLOB.bounty_hunter_entries, "Entry should be added to global list")
	
	// Тест удаления
	var/entry_id = test_entry.entry_id
	remove_bounty_entry(entry_id)
	TEST_ASSERT(!(test_entry in GLOB.bounty_hunter_entries), "Entry should be removed from global list")