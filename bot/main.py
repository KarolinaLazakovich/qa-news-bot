#!/usr/bin/env python3
import sys
from rss_fetcher import fetch_all_news
from digest_builder import build_digest
from telegram_sender import send_digest
from sent_cache import load_sent, save_sent


def main() -> None:
    print("=== QA News Digest Bot ===")

    print("\n[1/3] Fetching news from RSS feeds...")
    articles = fetch_all_news()
    print(f"      Total articles collected: {len(articles)}")

    sent_urls = load_sent()
    new_articles = [a for a in articles if a["url"] not in sent_urls]
    skipped = len(articles) - len(new_articles)
    print(f"      New (not sent before): {len(new_articles)} | Skipped duplicates: {skipped}")

    if not new_articles:
        print("\n⏭  No new articles today — skipping send.")
        return

    print("\n[2/3] Building digest...")
    digest = build_digest(new_articles)
    print(f"      Digest length: {len(digest)} chars")
    print("\n--- DIGEST PREVIEW ---")
    print(digest[:500] + ("..." if len(digest) > 500 else ""))
    print("--- END PREVIEW ---\n")

    print("[3/3] Sending to Telegram...")
    send_digest(digest)

    save_sent([a["url"] for a in new_articles])
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
