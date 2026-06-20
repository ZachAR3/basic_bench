extends SceneTree

func fail(message: String) -> void:
	push_error(message)
	quit(1)

func _initialize() -> void:
	var mode := OS.get_cmdline_user_args()[0]
	var bus = load("res://scripts/save_bus.gd").new()
	root.add_child(bus)
	if mode == "coalesce":
		var emitted: Array = []
		bus.save_requested.connect(func(generation, state): emitted.append([generation, state]))
		var first := {"nested": {"coins": 1}}
		bus.queue_save(first)
		first.nested.coins = 99
		bus.queue_save({"nested": {"coins": 2}})
		if emitted.size() != 0:
			return fail("queue_save emitted before flush")
		if bus.flush_pending() != 2 or emitted.size() != 1:
			return fail("latest generation was not coalesced")
		if emitted[0][1].nested.coins != 2:
			return fail("state was not deeply copied")
	elif mode == "stale":
		var finished: Array = []
		bus.save_finished.connect(func(generation, success): finished.append([generation, success]))
		var old_generation = bus.queue_save({"value": 1})
		var new_generation = bus.queue_save({"value": 2})
		bus.complete_save(old_generation, true)
		if not bus.dirty:
			return fail("stale completion cleared newer state")
		bus.complete_save(new_generation, false)
		if not bus.dirty:
			return fail("failed current save cleared dirty state")
		bus.complete_save(new_generation, true)
		if bus.dirty or finished.size() != 3:
			return fail("current success or completion signal failed")
	else:
		return fail("unknown mode")
	quit(0)
