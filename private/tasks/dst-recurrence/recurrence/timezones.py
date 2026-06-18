from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo


def _candidate_round_trips(naive, timezone, fold):
    candidate = naive.replace(tzinfo=timezone, fold=fold)
    round_trip = candidate.astimezone(UTC).astimezone(timezone)
    return round_trip.replace(tzinfo=None) == naive


def resolve_local(naive, timezone_name, gap_policy, overlap_policy):
    """Resolve one naive wall time or return None when a skipped gap is requested."""
    timezone = ZoneInfo(timezone_name)
    valid = [
        naive.replace(tzinfo=timezone, fold=fold)
        for fold in (0, 1)
        if _candidate_round_trips(naive, timezone, fold)
    ]
    unique = {candidate.astimezone(UTC): candidate for candidate in valid}
    ordered = [unique[key] for key in sorted(unique)]
    if ordered:
        return ordered[0] if overlap_policy == "earliest" else ordered[-1]
    if gap_policy == "skip":
        return None
    probe = naive
    for _ in range(24 * 60):
        probe += timedelta(minutes=1)
        for fold in (0, 1):
            if _candidate_round_trips(probe, timezone, fold):
                return probe.replace(tzinfo=timezone, fold=fold)
    raise ValueError("timezone gap exceeds one day")
