from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoint:
    scheme: str
    host: str
    port: int | None
    base_path: str
    username: str | None = None
    password: str | None = None

    @property
    def authority(self):
        host = f"[{self.host}]" if ":" in self.host else self.host
        return f"{host}:{self.port}" if self.port is not None else host
