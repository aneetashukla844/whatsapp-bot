from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# In-memory token counter and user list (resets every time app restarts)
token_counter = 1
appointments = {}

@app.route("/bot", methods=["POST"])
def bot():
    global token_counter

    incoming_msg = request.values.get('Body', '').strip()
    phone_number = request.values.get('From', '')
    user_name = incoming_msg
    response = MessagingResponse()
    message = response.message()

    if incoming_msg.lower() == "hi":
        message.body("👋 Welcome to Dr. Sharma's Clinic!

Please type '1' to book an appointment.")
    elif incoming_msg == "1":
        message.body("✅ Please enter your *full name* to book your appointment.")
        appointments[phone_number] = {"status": "awaiting_name"}
    elif phone_number in appointments and appointments[phone_number]["status"] == "awaiting_name":
        # Save name and assign token
        appointments[phone_number]["name"] = user_name
        appointments[phone_number]["status"] = "confirmed"
        appointments[phone_number]["token"] = token_counter
        token_msg = f"📝 Appointment Confirmed!

Name: {user_name}
Phone: {phone_number[-10:]}
Token No: {token_counter}"
        token_counter += 1
        message.body(token_msg)
    else:
        message.body("❓ I didn't understand that. Please type 'hi' to start.")

    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
