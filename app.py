from flask import Flask, request
import requests
import os
from openai import OpenAI

# Cliente OpenAI (API nueva)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


WHATSAPP_TOKEN = os.getenv("WA_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")

app = Flask(__name__)

SYSTEM_PROMPT = """
Eres el vendedor oficial de la marca de ropa deportiva Raios⚡.
Vendes camisetas y esqueletos para gimnasio.
Tu tono es energético, motivador y profesional.
Usas emojis ⚡🔥💪 con moderación.
Siempre preguntas talla, color y ciudad.
Siempre intentas cerrar la venta.
Nunca digas que eres una IA.
Productos:
- Camiseta Pro: 45.000 COP, tallas S M L XL, colores negro gris blanco
- Esqueleto Gym: 40.000 COP, tallas S M L XL, colores negro gris
Envíos a toda Colombia.
"""

def send_whatsapp_message(phone, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        phone = message["from"]
        text = message["text"]["body"]

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
        )

        reply = completion.choices[0].message.content

        send_whatsapp_message(phone, reply)

    except Exception as e:
        print("Error:", e)

    return "ok", 200


@app.route("/", methods=["GET"])
def home():
    return "Raios⚡ WhatsApp Bot Online", 200
