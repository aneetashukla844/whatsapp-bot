from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

token_counter = 1
appointments = {}

@app.route("/bot", methods=["POST"])
def bot():
    global token_counter

    incoming_msg = request.values.get('Body', '').strip()
    phone_number = request.values.get('From', '')
    response = MessagingResponse()
    message = response.message()

    if incoming_msg.lower() == "hi":
        message.body("👋 Welcome to Dr. Sharma's Clinic!\n\nPlease type '1' to book an appointment.")
    elif incoming_msg == "1":
        message.body("✅ Please enter your *full name* to book your appointment.")
        appointments[phone_number] = {"status": "awaiting_name"}
    elif phone_number in appointments and appointments[phone_number]["status"] == "awaiting_name":
        # Save name and assign token
        user_name = incoming_msg
        appointments[phone_number]["name"] = user_name
        appointments[phone_number]["status"] = "confirmed"
        appointments[phone_number]["token"] = token_counter
        token_msg = f"📝 Appointment Confirmed!\n\nName: {user_name}\nPhone: {phone_number[-10:]}\nToken No: {token_counter}"
        token_counter += 1
        message.body(token_msg)
    else:
        message.body("❓ I didn't understand that. Please type 'hi' to start.")

    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
