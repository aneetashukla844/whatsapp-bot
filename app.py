from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/bot", methods=["POST"])
def bot():
    msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg_reply = resp.message()

    if msg == "hi":
        msg_reply.body("👋 Welcome! Type 1 to book an appointment.")
    elif msg == "1":
        msg_reply.body("📅 Please enter your full name to continue.")
    else:
        msg_reply.body("❓ I didn't understand. Type 'hi' to begin.")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
