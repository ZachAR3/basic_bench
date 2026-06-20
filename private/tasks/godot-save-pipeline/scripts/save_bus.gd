class_name SaveBus
extends Node

signal save_requested(generation: int, state: Dictionary)
signal save_finished(generation: int, success: bool)

var generation := 0
var dirty := false
var pending_state: Dictionary = {}

func queue_save(state: Dictionary) -> int:
	generation += 1
	dirty = true
	pending_state = state
	save_requested.emit(generation, state)
	return generation

func flush_pending() -> int:
	save_requested.emit(generation, pending_state)
	return generation

func complete_save(completed_generation: int, success: bool) -> void:
	if success:
		dirty = false
	save_finished.emit(completed_generation, success)
