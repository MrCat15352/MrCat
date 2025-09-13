//Integration tests for orbital system

#ifdef TESTING

/datum/unit_test/orbital_system_basic
	name = "Orbital System - Basic Functionality"

/datum/unit_test/orbital_system_basic/Run()
	//Test subsystem initialization
	if(!SSorbits)
		TEST_FAIL("SSorbits subsystem not found")
		return
	
	if(!SSorbits.initialized)
		TEST_FAIL("SSorbits not initialized")
		return
	
	//Test orbital map creation
	if(!length(SSorbits.orbital_maps))
		TEST_FAIL("No orbital maps created")
		return
	
	var/datum/orbital_map/primary_map = SSorbits.orbital_maps[PRIMARY_ORBITAL_MAP]
	if(!primary_map)
		TEST_FAIL("Primary orbital map not found")
		return
	
	TEST_PASS("Basic orbital system functionality working")

/datum/unit_test/orbital_objects
	name = "Orbital System - Object Creation"

/datum/unit_test/orbital_objects/Run()
	//Test object creation
	var/datum/orbital_object/test_obj = new /datum/orbital_object/planet(new /datum/orbital_vector(0, 0))
	
	if(!test_obj)
		TEST_FAIL("Failed to create orbital object")
		return
	
	if(!test_obj.unique_id)
		TEST_FAIL("Orbital object missing unique ID")
		return
	
	//Test object is added to map
	var/datum/orbital_map/primary_map = SSorbits.orbital_maps[PRIMARY_ORBITAL_MAP]
	var/list/all_bodies = primary_map.get_all_bodies()
	
	if(!(test_obj in all_bodies))
		TEST_FAIL("Orbital object not added to map")
		return
	
	//Cleanup
	qdel(test_obj)
	TEST_PASS("Orbital object creation working")

/datum/unit_test/orbital_vectors
	name = "Orbital System - Vector Math"

/datum/unit_test/orbital_vectors/Run()
	var/datum/orbital_vector/vec1 = new /datum/orbital_vector(3, 4)
	var/datum/orbital_vector/vec2 = new /datum/orbital_vector(1, 2)
	
	//Test basic operations
	if(vec1.Length() != 5)
		TEST_FAIL("Vector length calculation incorrect: expected 5, got [vec1.Length()]")
		return
	
	var/datum/orbital_vector/vec3 = vec1.Add(vec2)
	if(vec3.GetX() != 4 || vec3.GetY() != 6)
		TEST_FAIL("Vector addition incorrect: expected (4,6), got ([vec3.GetX()],[vec3.GetY()])")
		return
	
	var/distance = vec1.DistanceTo(vec2)
	if(abs(distance - 2.828) > 0.01)
		TEST_FAIL("Vector distance calculation incorrect: expected ~2.828, got [distance]")
		return
	
	TEST_PASS("Vector math working correctly")

/datum/unit_test/orbital_ui
	name = "Orbital System - UI Integration"

/datum/unit_test/orbital_ui/Run()
	//Test UI data generation
	var/datum/orbital_map/primary_map = SSorbits.orbital_maps[PRIMARY_ORBITAL_MAP]
	var/data = SSorbits.get_orbital_map_base_data(primary_map, "test_user")
	
	if(!islist(data))
		TEST_FAIL("UI data is not a list")
		return
	
	if(!("map_objects" in data))
		TEST_FAIL("UI data missing map_objects")
		return
	
	if(!("update_index" in data))
		TEST_FAIL("UI data missing update_index")
		return
	
	TEST_PASS("UI integration working")

#endif