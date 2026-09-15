import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WAHA_URL = os.getenv("WAHA_URL")
WAHA_API_KEY = os.getenv("WAHA_API_KEY")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")
WHATSAPP_CHANNEL_ID = os.getenv("WHATSAPP_CHANNEL_ID")

TELEGRAM_SECRET = os.getenv("TELEGRAM_SECRET", "")


def send_to_whatsapp(text):
    url = f"{WAHA_URL.rstrip('/')}/api/sendText"

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": WAHA_API_KEY
    }

    data = {
        "session": WAHA_SESSION,
        "chatId": WHATSAPP_CHANNEL_ID,
        "text": text,
        "linkPreview": True
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=30
    )

    print("WAHA:", response.status_code, response.text)

    return response.ok


@app.route("/", methods=["GET"])
def home():
    return "Loot Deals Telegram → WhatsApp Bridge is running!"


@app.route("/telegram", methods=["POST"])
def telegram_webhook():

    if TELEGRAM_SECRET:
        received_secret = request.headers.get(
            "X-Telegram-Bot-Api-Secret-Token"
        )

        if received_secret != TELEGRAM_SECRET:
            return jsonify({"ok": False}), 403

    update = request.get_json(silent=True) or {}

    post = update.get("channel_post")

    if not post:
        return jsonify({"ok": True})

    chat = post.get("chat", {})
    username = chat.get("username", "")

    # শুধুমাত্র Loot Deals channel থেকে পোস্ট গ্রহণ
    if username.lower() != "loot_dells":
        return jsonify({"ok": True})

    text = post.get("text") or post.get("caption") or ""

    if not text:
        return jsonify({"ok": True})

    success = send_to_whatsapp(text)

    return jsonify({
        "ok": success
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(
        host="0.0.0.0",
        port=port
    )
