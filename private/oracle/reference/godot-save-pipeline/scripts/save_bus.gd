class_name SaveBus
extends Node

signal save_requested(generation: int, state: Dictionary)
signal save_finished(generation: int, success: bool)

var generation := 0
var dirty := false
var pending_state: Dictionary = {}
var _has_pending := false

func queue_save(state: Dictionary) -> int:
	generation += 1
	dirty = true
	pending_state = state.duplicate(true)
	_has_pending = true
	return generation

func flush_pending() -> int:
	if _has_pending:
		save_requested.emit(generation, pending_state.duplicate(true))
		_has_pending = false
	return generation

func complete_save(completed_generation: int, success: bool) -> void:
	if completed_generation == generation and success:
		dirty = false
	save_finished.emit(completed_generation, success)
