A Godot save pipeline loses newer state when asynchronous saves finish out of
order, and its C# persistence layer can leave corrupt files. Repair both the
typed GDScript coordinator and the C# repository.

Requirements:

- `SaveBus.queue_save` must deep-copy state, coalesce queued work, and emit only
  when `flush_pending` is called. Each queued state receives a monotonic
  generation.
- A completion for an older generation must never clear newer dirty state.
  Failed current saves remain dirty. Completion signals still identify the
  generation that finished.
- Keep valid Godot 4.x typed GDScript syntax and the existing signal names.
- C# slot names accept only ASCII letters, digits, `_`, and `-`; traversal,
  separators, empty names, and Unicode lookalikes are rejected.
- Saves write JSON to a unique temporary file and atomically replace the final
  file. Cancellation or failure cleans up the temporary file.
- Loading migrates version 1 data to version 2 by renaming `coins` to
  `currency`, preserves unknown fields, rejects future versions, and returns
  data that does not share mutable state across calls.
- Keep the C# project dependency-free and preserve the public API.

No tests are provided. Do not add generated Godot or .NET build artifacts.
