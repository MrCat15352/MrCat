//Shuttle data for orbital system

/datum/shuttle_data
	var/port_id
	var/shuttle_name = "Неизвестный шаттл"
	var/fuel = 100
	var/max_fuel = 100
	var/thrust = 0
	var/max_thrust = 10
	var/angle = 0
	var/autopilot_enabled = FALSE
	var/breaking = FALSE

/datum/shuttle_data/New(port_id)
	src.port_id = port_id
	// Simplified shuttle name assignment
	shuttle_name = "Shuttle [port_id]"

/datum/shuttle_data/proc/get_fuel_percentage()
	return (fuel / max_fuel) * 100

/datum/shuttle_data/proc/consume_fuel(amount)
	fuel = max(0, fuel - amount)
	return fuel > 0