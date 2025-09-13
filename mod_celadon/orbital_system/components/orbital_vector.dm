//Orbital vectors
/datum/orbital_vector
	VAR_PRIVATE/x = 0
	VAR_PRIVATE/y = 0
	var/protected = FALSE

/datum/orbital_vector/New(_x = 0, _y = 0)
	. = ..()
	x = _x
	y = _y

/datum/orbital_vector/proc/Set(x, y)
	if(protected)
		CRASH("Attempted to translate a protected vector.")
	src.x = x
	src.y = y

/datum/orbital_vector/proc/SetUnsafely(x, y)
	src.x = x
	src.y = y

/datum/orbital_vector/proc/GetX()
	return x

/datum/orbital_vector/proc/GetY()
	return y

//Returns a new vector equal to the current vector + other
/datum/orbital_vector/proc/Add(datum/orbital_vector/other)
	return new /datum/orbital_vector(
		other.x + x,
		other.y + y
	)

//Returns a new vector equal to the current vector * scalar_amount
/datum/orbital_vector/proc/Scale(scalar_amount)
	return new /datum/orbital_vector(
		x * scalar_amount,
		y * scalar_amount
	)

//Adds the other vector to our current vector.
/datum/orbital_vector/proc/AddSelf(datum/orbital_vector/other)
	if(protected)
		CRASH("Attempted to translate a protected vector.")
	src.x += other.x
	src.y += other.y
	return src

//Scales our current vector by a scalar amount
/datum/orbital_vector/proc/ScaleSelf(scalar_amount)
	if(protected)
		CRASH("Attempted to scale a protected vector.")
	x *= scalar_amount
	y *= scalar_amount
	return src

//Returns magnitude of the vector
/datum/orbital_vector/proc/Length()
	return sqrt(x * x + y * y)

//Returns distanace between 2 positional vectors
/datum/orbital_vector/proc/DistanceTo(datum/orbital_vector/other)
	var/delta_x = other.x - x
	var/delta_y = other.y - y
	return sqrt(delta_x * delta_x + delta_y * delta_y)

//Make the vector length 1
/datum/orbital_vector/proc/NormalizeSelf()
	if(protected)
		CRASH("Attempted to normalize a protected vector.")
	var/total = Length()
	if(!total)
		x = 0
		y = 1
		return src
	x = x / total
	y = y / total
	return src

/datum/orbital_vector/proc/RotateSelf(angle)
	if(protected)
		CRASH("Attempted to rotate a protected vector.")
	var/_x = x
	x = x * cos(angle) - y * sin(angle)
	y = _x * sin(angle) + y * cos(angle)
	return src