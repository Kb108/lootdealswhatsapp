import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

WAHA_URL = os.getenv("WAHA_URL", "")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")
WHATSAPP_CHANNEL_ID = os.getenv("WHATSAPP_CHANNEL_ID", "")


def send_to_whatsapp(text):
    if not WAHA_URL or not WHATSAPP_CHANNEL_ID:
        print("WhatsApp settings are not configured yet.")
        return False

    url = f"{WAHA_URL.rstrip('/')}/api/sendText"

    headers = {
        "Content-Type": "application/json"
    }

    if WAHA_API_KEY:
        headers["X-Api-Key"] = WAHA_API_KEY

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

    print("WhatsApp response:", response.status_code, response.text)

    return response.ok


@app.route("/", methods=["GET"])
def home():
    return "Loot Deals Telegram → WhatsApp Bridge is running!"


@app.route("/telegram", methods=["POST"])
def telegram_webhook():

    update = request.get_json(silent=True) or {}

    print("Telegram update received:")
    print(update)

    post = update.get("channel_post")

    if not post:
        return jsonify({"ok": True})

    text = post.get("text") or post.get("caption")

    if not text:
        return jsonify({"ok": True})

    print("Loot Deals post:")
    print(text)

    # WhatsApp এখনো সেটআপ না হলেও Telegram message receive test হবে
    send_to_whatsapp(text)

    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
