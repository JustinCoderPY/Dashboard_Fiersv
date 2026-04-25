from datetime import datetime, timezone


def get_utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

