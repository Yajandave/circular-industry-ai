"""Bounded, privacy-minimised API event metrics for local diagnostics."""
from collections import deque
from datetime import datetime, timezone
from threading import Lock

_events = deque(maxlen=250)
_lock = Lock()

def record(path: str, method: str, status: int, elapsed_ms: int, exception_type: str | None = None):
    # Discard dynamic IDs, queries, bodies, auth headers, messages and stack traces.
    parts = path.split("?")[0].split("/")
    group = "/" + "/".join([part for part in parts if part][:2])
    event = {
        "time": datetime.now(timezone.utc).isoformat(),
        "endpoint_group": group,
        "method": method.upper(),
        "status": status,
        "duration_ms": elapsed_ms,
        "error_type": exception_type,
    }
    with _lock:
        _events.append(event)

def snapshot():
    with _lock:
        return list(_events)
