An offline-capable inventory screen has correctness bugs that appear under
React concurrent rendering and unreliable networks. Repair the implementation
without adding dependencies or changing the public exports.

Requirements:

- `getSnapshot` must return a referentially stable, immutable snapshot until
  store state changes. Callers must not be able to mutate internal items.
- Optimistic updates may overlap. A late success or failure for an older
  request must not overwrite a newer edit. Rejecting the newest request must
  restore the state that existed immediately before that request.
- Server refreshes must not replace items that currently have local optimistic
  edits, and older server revisions must be ignored.
- URL filters must round-trip Unicode, repeated warehouse values, empty state,
  and deterministic ordering. Unknown parameters must be preserved.
- Search must abort obsolete requests, ignore stale completions even when the
  API does not honor abort, suppress abort errors, expose non-abort failures
  accessibly, and avoid a request for an empty trimmed query.
- Keep the project buildable as a production Vite/React application.

No tests are provided. Keep the repair focused on `src/`.
