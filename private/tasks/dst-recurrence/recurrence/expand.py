from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from .model import DailyRule


def expand_daily(start_date, rule: DailyRule):
    """Return ``rule.count`` timezone-aware daily occurrences."""
    timezone = ZoneInfo(rule.timezone)
    first_local = datetime.combine(start_date, rule.local_time, timezone)
    first_utc = first_local.astimezone(UTC)
    return [
        (first_utc + timedelta(days=offset)).astimezone(timezone)
        for offset in range(rule.count)
    ]
