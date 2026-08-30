TIERS = [
    {"name": "tier0", "model": "openai/gpt-oss-20b", "accept_threshold": 0.75},
    {"name": "tier1", "model": "openai/gpt-oss-120b", "accept_threshold": 0.0},  # last resort, always accept
]
