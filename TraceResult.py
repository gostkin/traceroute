from dataclasses import dataclass
import typing as tp


@dataclass
class TraceResult:
    ttl: int
    resolved: bool = False
    hostname: tp.Optional[str] = None
    addr: tp.Optional[str] = None
    finished: bool = False
    time: float = 0.0
