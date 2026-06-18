# Recurrence expansion

This package expands a daily wall-clock rule into timezone-aware datetimes.

Important semantics:

- A daily rule means the same local clock reading, not a fixed 24-hour UTC interval.
- `gap_policy="forward"` moves a nonexistent local time to the first valid local minute.
- `gap_policy="skip"` omits dates whose configured local time does not exist.
- `overlap_policy="earliest"` chooses the first instant represented by an ambiguous wall time.
- `overlap_policy="latest"` chooses the second instant.
- Returned datetimes retain the requested `ZoneInfo` timezone.
- The requested count is the number of returned occurrences; skipped dates do not consume it.

The timezone resolver owns gap/overlap detection. Expansion code should call it rather than
trying to infer transitions from UTC offsets.
