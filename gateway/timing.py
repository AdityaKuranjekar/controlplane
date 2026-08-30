import time
from contextlib import contextmanager

class Stopwatch:
    def __init__(self):
        self.stages: dict[str, float] = {}

    @contextmanager
    def measure(self, stage_name: str):
        start = time.perf_counter()
        yield
        self.stages[stage_name] = round((time.perf_counter() - start) * 1000, 2)  # ms

    def as_headers(self) -> dict:
        headers = {f"X-CP-{k}-ms": str(v) for k, v in self.stages.items()}
        headers["X-CP-Total-ms"] = str(round(sum(self.stages.values()), 2))
        return headers
