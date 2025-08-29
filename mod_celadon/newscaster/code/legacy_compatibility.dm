// Legacy compatibility file for old newscaster references
// This file provides type compatibility for old datum/newscaster/* references

// Legacy type compatibility - create actual types that inherit from new ones
/datum/newscaster

/datum/newscaster/feed_channel
	parent_type = /datum/feed_channel

/datum/newscaster/feed_message
	parent_type = /datum/feed_message

/datum/newscaster/feed_comment
	parent_type = /datum/feed_comment

/datum/newscaster/wanted_message
	parent_type = /datum/wanted_message