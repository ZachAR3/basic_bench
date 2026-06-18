from datetime import datetime, timedelta

from .model import DailyRule
from .timezones import resolve_local


def expand_daily(start_date, rule: DailyRule):
    """Return ``rule.count`` timezone-aware daily occurrences."""
    occurrences = []
    current_date = start_date
    while len(occurrences) < rule.count:
        naive = datetime.combine(current_date, rule.local_time)
        resolved = resolve_local(
            naive,
            rule.timezone,
            gap_policy=rule.gap_policy,
            overlap_policy=rule.overlap_policy,
        )
        if resolved is not None:
            occurrences.append(resolved)
        current_date += timedelta(days=1)
    return occurrences
