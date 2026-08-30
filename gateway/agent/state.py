"""
Simulates optimistic concurrency control: every mutable resource has a
version tag (ETag).
"""

RESOURCE_VERSIONS = {
    "record_101": "etag_v1",
    "record_202": "etag_v1",
}

def current_etag(resource_id: str) -> str | None:
    return RESOURCE_VERSIONS.get(resource_id)

def is_stale(resource_id: str, provided_etag: str | None) -> bool:
    if provided_etag is None:
        return False
    return current_etag(resource_id) != provided_etag

def simulate_external_drift(resource_id: str):
    """Test helper: simulates the resource changing underneath the agent."""
    RESOURCE_VERSIONS[resource_id] = "etag_v2_drifted"
