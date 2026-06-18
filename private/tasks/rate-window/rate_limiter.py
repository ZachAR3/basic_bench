from collections import deque


class SlidingWindowLimiter:
    def __init__(self, limit, window_seconds):
        if limit < 1 or window_seconds <= 0:
            raise ValueError("invalid limiter settings")
        self.limit = limit
        self.window_seconds = window_seconds
        self.events = deque()

    def allow(self, now):
        cutoff = now - self.window_seconds
        while self.events and self.events[0] < cutoff:
            self.events.popleft()
        self.events.append(now)
        return len(self.events) <= self.limit
