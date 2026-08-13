import logging

import httpx

from config import get_secret

SLACK_TOKEN = get_secret("SLACK_BOT_TOKEN")
SLACK_CHANNEL = get_secret("SLACK_CHANNEL")
HEADERS = {"Authorization": f"Bearer {SLACK_TOKEN}"}

logger = logging.getLogger(__name__)


def post_slack_message(text: str, username: str | None = None) -> dict:
    # Posting under a human-looking username needs the chat:write.customize
    # scope; without it fixture messages appear as the analyzer bot itself,
    # which the skill discounts as seed data.
    payload = {"channel": SLACK_CHANNEL, "text": text}
    if username:
        payload["username"] = username
        payload["icon_emoji"] = ":technologist:"

    resp = httpx.post(
        "https://slack.com/api/chat.postMessage",
        headers=HEADERS,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()

    if not data.get("ok") and data.get("error") == "missing_scope" and username:
        logger.warning(
            "Slack app lacks the chat:write.customize scope; "
            "posting fixture as the bot's own identity instead"
        )
        return post_slack_message(text)

    if not data.get("ok"):
        raise RuntimeError(f"Slack postMessage failed: {data}")
    return {"ts": data["ts"], "channel": data["channel"]}


def delete_slack_message(channel: str, ts: str) -> None:
    resp = httpx.post(
        "https://slack.com/api/chat.delete",
        headers=HEADERS,
        json={"channel": channel, "ts": ts},
    )
    resp.raise_for_status()
