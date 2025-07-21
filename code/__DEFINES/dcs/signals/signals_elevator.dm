// Elevator signals

/// Sent when an elevator platform is about to travel to a new location: (obj/structure/elevator_platform/platform, turf/destination)
#define COMSIG_GLOB_ELEVATOR_PLATFORM_TRAVEL "!elevator_platform_travel"
/// Return this to cancel the default elevator travel behavior
#define COMPONENT_CANCEL_ELEVATOR_TRAVEL (1<<0)