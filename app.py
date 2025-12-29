from flask import Flask, request
import requests
import os
from openai import OpenAI

app = Flask(__name__)

# Tokens
VERIFY_TOKEN = "raios123"
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# Webhook verification
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Error", 403

# Receive messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        phone = message["from"]
        text = message["text"]["body"]

        ai = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"Eres el asistente de ventas de la marca Raios, ropa deportiva para hombres. Responde corto, persuasivo y profesional."},
                {"role":"user","content":text}
            ]
        )

        reply = ai.choices[0].message.content

        url = "https://graph.facebook.com/v19.0/" + os.getenv("PHONE_ID") + "/messages"
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

    except:
        pass

    return "ok", 200

# KEEP SERVER ALIVE FOR RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
