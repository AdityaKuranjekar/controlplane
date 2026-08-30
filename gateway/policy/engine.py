import yaml
from pathlib import Path
from functools import lru_cache

PROFILE_DIR = Path(__file__).parent / "profiles"

@lru_cache(maxsize=8)
def get_profile(name: str) -> dict:
    path = PROFILE_DIR / f"{name}.yaml"
    if not path.exists():
        raise ValueError(f"Unknown profile: {name}")
    return yaml.safe_load(path.read_text())
