from flask import Flask, request
import requests
import os
from openai import OpenAI

app = Flask(__name__)

VERIFY_TOKEN = "raios123"

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

@app.route("/", methods=["GET"])
def home():
    return "Raios WhatsApp Bot Online", 200

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        phone = msg["from"]
        text = msg["text"]["body"]

        ai = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"Eres el asistente de ventas de Raios, una marca de ropa deportiva masculina. Responde de forma corta, persuasiva y profesional."},
                {"role":"user","content": text}
            ]
        )

        reply = ai.choices[0].message.content

        url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": reply}
        }

        requests.post(url, headers=headers, json=payload)

    except Exception as e:
        print(e)

    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
