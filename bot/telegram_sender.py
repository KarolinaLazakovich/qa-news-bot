import os
import httpx


TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"
MAX_MSG_LEN = 4000  # Telegram limit is 4096, keep some margin


def send_digest(text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    chunks = _split_message(text)

    with httpx.Client(timeout=30) as client:
        for i, chunk in enumerate(chunks):
            url = TELEGRAM_API.format(token=token, method="sendMessage")
            payload = {
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }
            resp = client.post(url, json=payload)
            if not resp.is_success:
                print(f"Telegram error on chunk {i}: {resp.text}")
                # Retry without markdown if parsing failed
                if "parse" in resp.text.lower():
                    payload["parse_mode"] = None
                    client.post(url, json=payload)
                else:
                    resp.raise_for_status()

    print(f"Digest sent ({len(chunks)} message(s))")


def _split_message(text: str) -> list[str]:
    if len(text) <= MAX_MSG_LEN:
        return [text]

    chunks = []
    while text:
        if len(text) <= MAX_MSG_LEN:
            chunks.append(text)
            break

        split_at = text.rfind("\n", 0, MAX_MSG_LEN)
        if split_at == -1:
            split_at = MAX_MSG_LEN

        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()

    return chunks
