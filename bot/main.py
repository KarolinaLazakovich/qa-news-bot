#!/usr/bin/env python3
import sys
from rss_fetcher import fetch_all_news
from digest_builder import build_digest
from telegram_sender import send_digest


def main() -> None:
    print("=== QA News Digest Bot ===")

    print("\n[1/3] Fetching news from RSS feeds...")
    articles = fetch_all_news()
    print(f"      Total articles collected: {len(articles)}")

    print("\n[2/3] Building digest with Claude...")
    digest = build_digest(articles)
    print(f"      Digest length: {len(digest)} chars")
    print("\n--- DIGEST PREVIEW ---")
    print(digest[:500] + ("..." if len(digest) > 500 else ""))
    print("--- END PREVIEW ---\n")

    print("[3/3] Sending to Telegram...")
    send_digest(digest)

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
