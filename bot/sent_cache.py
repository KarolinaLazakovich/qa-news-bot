import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

CACHE_PATH = Path(__file__).parent.parent / "sent_urls.json"
MAX_AGE_DAYS = 14


def load_sent() -> set[str]:
    if not CACHE_PATH.exists():
        return set()
    try:
        data = json.loads(CACHE_PATH.read_text())
        cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
        return {url for url, ts in data.items()
                if datetime.fromisoformat(ts) > cutoff}
    except Exception:
        return set()


def save_sent(urls: list[str]) -> None:
    existing: dict[str, str] = {}
    if CACHE_PATH.exists():
        try:
            existing = json.loads(CACHE_PATH.read_text())
        except Exception:
            pass

    now = datetime.now(timezone.utc).isoformat()
    for url in urls:
        existing[url] = now

    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    existing = {url: ts for url, ts in existing.items()
                if datetime.fromisoformat(ts) > cutoff}

    CACHE_PATH.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
