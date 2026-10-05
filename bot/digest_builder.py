import httpx
from datetime import datetime, date


CATEGORIES = {
    "mobile_testing": "📱 *Мобильное тестирование*",
    "ai_testing":     "🤖 *ИИ в тестировании*",
    "qa_general":     "🔧 *QA & Автоматизация*",
    "pentesting":     "🔐 *Пентест & Безопасность*",
}

# confs.tech GitHub raw data — free, no API key
CONFS_TECH_TOPICS = ["testing", "devops"]
CONFS_TECH_URL = (
    "https://raw.githubusercontent.com/tech-conferences/conference-data"
    "/main/conferences/{year}/{topic}.json"
)
CONF_LOOKAHEAD_DAYS = 120

# Rotating daily learning resources (by weekday: 0=Monday … 4=Friday)
DAILY_RESOURCES = [
    ("PortSwigger Web Security Academy", "https://portswigger.net/web-security"),
    ("OWASP Mobile Testing Guide (MASTG)", "https://mas.owasp.org/MASTG/"),
    ("Google Testing Blog", "https://testing.googleblog.com/"),
    ("Ministry of Testing — Articles", "https://www.ministryoftesting.com/articles"),
    ("Awesome Testing (curated list)", "https://github.com/TheJambo/awesome-testing"),
]


def build_digest(articles: list[dict]) -> str:
    today = datetime.now().strftime("%d.%m.%Y")
    lines = [f"*🗞 QA-дайджест | {today}*\n"]

    by_category: dict[str, list[dict]] = {cat: [] for cat in CATEGORIES}
    for article in articles:
        cat = article.get("category", "qa_general")
        if cat in by_category:
            by_category[cat].append(article)

    for cat, label in CATEGORIES.items():
        cat_articles = by_category[cat]
        if not cat_articles:
            continue

        # Русские статьи в приоритете, потом английские; максимум 6 на категорию
        ru = [a for a in cat_articles if a["lang"] == "ru"]
        en = [a for a in cat_articles if a["lang"] != "ru"]
        ordered = (ru + en)[:6]

        lines.append(label)
        for a in ordered:
            lang_tag = "`[RU]` " if a["lang"] == "ru" else ""
            lines.append(f"• {lang_tag}[{a['title'].strip()}]({a['url']}) — _{a['source']}_")
        lines.append("")

    conferences = _fetch_conferences()
    if conferences:
        lines.append("🎓 *Конференции*")
        lines.extend(conferences)
        lines.append("")

    lines.extend(_daily_resource())

    return "\n".join(lines)


def _fetch_conferences() -> list[str]:
    today = date.today()
    results = []

    for topic in CONFS_TECH_TOPICS:
        for year in {today.year, today.year + 1}:
            url = CONFS_TECH_URL.format(year=year, topic=topic)
            try:
                resp = httpx.get(url, timeout=10)
                if not resp.is_success:
                    continue
                for conf in resp.json():
                    start = _parse_date(conf.get("startDate", ""))
                    if start is None:
                        continue
                    days_away = (start - today).days
                    if not (0 <= days_away <= CONF_LOOKAHEAD_DAYS):
                        continue

                    name = conf.get("name", "")
                    conf_url = conf.get("url", "")
                    city = conf.get("city", "")
                    country = conf.get("country", "")
                    online = conf.get("online", False)

                    location = "онлайн" if online else f"{city}, {country}".strip(", ")
                    date_str = start.strftime("%d.%m.%Y")

                    link = f"[{name}]({conf_url})" if conf_url else name
                    results.append(f"• {link} | {date_str} | {location}")
            except Exception as e:
                print(f"Conferences fetch error ({topic}/{year}): {e}")

    return results


def _daily_resource() -> list[str]:
    weekday = date.today().weekday()  # 0=Mon, 4=Fri
    name, url = DAILY_RESOURCES[weekday % len(DAILY_RESOURCES)]
    return [f"📚 *Почитай на этой неделе*", f"• [{name}]({url})", ""]


def _parse_date(value: str) -> date | None:
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            return datetime.strptime(value[:len(fmt)], fmt).date()
        except ValueError:
            continue
    return None
