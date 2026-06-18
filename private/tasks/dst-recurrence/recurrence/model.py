from dataclasses import dataclass
from datetime import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True)
class DailyRule:
    local_time: time
    timezone: str
    count: int
    gap_policy: str = "forward"
    overlap_policy: str = "earliest"

    def __post_init__(self):
        if self.local_time.tzinfo is not None:
            raise ValueError("local_time must be naive")
        if self.count < 1:
            raise ValueError("count must be positive")
        if self.gap_policy not in {"forward", "skip"}:
            raise ValueError("unsupported gap policy")
        if self.overlap_policy not in {"earliest", "latest"}:
            raise ValueError("unsupported overlap policy")
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"unknown timezone: {self.timezone}") from exc
