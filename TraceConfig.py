from dataclasses import dataclass


@dataclass
class TraceConfig:
    start_port: int = 33434
    max_probs: int = 3
    response_timeout_sec: float = 5.0
    max_ttl: int = 30
    source_address: str = ""
    json: bool = False
