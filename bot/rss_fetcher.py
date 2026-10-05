import re
import httpx
import feedparser
import yaml
from datetime import datetime, timezone, timedelta
from pathlib import Path


SOURCES_PATH = Path(__file__).parent.parent / "sources.yaml"
DEFAULT_LOOKBACK_HOURS = 48
MAX_PER_SOURCE = 2


def fetch_all_news() -> list[dict]:
    with open(SOURCES_PATH) as f:
        config = yaml.safe_load(f)

    articles = []

    for category, feeds in config["feeds"].items():
        for feed_config in feeds:
            lookback = feed_config.get("lookback_hours", DEFAULT_LOOKBACK_HOURS)
            cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback)
            try:
                feed_articles = _fetch_feed(feed_config, category, cutoff)
                articles.extend(feed_articles)
                print(f"  ✓ {feed_config['name']}: {len(feed_articles)} articles")
            except Exception as e:
                print(f"  ✗ {feed_config['name']}: {e}")

    return _deduplicate(articles)


def _deduplicate(articles: list[dict]) -> list[dict]:
    """Дедупликация по URL и нормализованному заголовку. Русский источник в приоритете."""
    seen_urls: dict[str, dict] = {}
    seen_titles: dict[str, dict] = {}

    def _norm_title(t: str) -> str:
        import re
        return re.sub(r"\W+", " ", t.lower()).strip()

    for a in articles:
        url = a["url"]
        title_key = _norm_title(a["title"])

        # Проверяем дубль по URL
        if url in seen_urls:
            if a["lang"] == "ru" and seen_urls[url]["lang"] != "ru":
                seen_urls[url] = a
            continue

        # Проверяем дубль по заголовку (Dev.to постит одно и то же с разными slug)
        if title_key in seen_titles:
            if a["lang"] == "ru" and seen_titles[title_key]["lang"] != "ru":
                old = seen_titles[title_key]
                seen_urls.pop(old["url"], None)
                seen_titles[title_key] = a
                seen_urls[url] = a
            continue

        seen_urls[url] = a
        seen_titles[title_key] = a

    return list(seen_urls.values())


def _fetch_feed(feed_config: dict, category: str, cutoff: datetime) -> list[dict]:
    with httpx.Client(timeout=15, follow_redirects=True) as client:
        resp = client.get(
            feed_config["url"],
            headers={"User-Agent": "Mozilla/5.0 QA-News-Bot/1.0"},
        )
        resp.raise_for_status()

    feed = feedparser.parse(resp.text)
    articles = []

    for entry in feed.entries[:30]:
        pub = entry.get("published_parsed") or entry.get("updated_parsed")
        if pub:
            pub_dt = datetime(*pub[:6], tzinfo=timezone.utc)
            if pub_dt < cutoff:
                continue
            date_str = pub_dt.strftime("%d.%m.%Y")
        else:
            date_str = "?"

        raw_summary = entry.get("summary", entry.get("description", ""))
        summary = re.sub(r"<[^>]+>", " ", raw_summary).strip()
        summary = re.sub(r"\s+", " ", summary)[:600]

        articles.append(
            {
                "source": feed_config["name"],
                "category": category,
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", ""),
                "summary": summary,
                "date": date_str,
                "lang": feed_config.get("lang", "en"),
            }
        )
        if len(articles) >= MAX_PER_SOURCE:
            break

    return articles
