from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

token_counter = 1
appointments = {}  # Stores phone_number -> info

@app.route("/bot", methods=["POST"])
def bot():
    global token_counter

    incoming_msg = request.values.get('Body', '').strip()
    phone_number = request.values.get('From', '')
    response = MessagingResponse()
    message = response.message()

    # Step 1: Start
    if incoming_msg.lower() == "hi,hii,hiii":
        message.body("👋 Welcome to DB Shukla's Clinic!\n\nPlease type '1' to book an appointment.")

    # Step 2: Ask for Name
    elif incoming_msg == "1":
        message.body("✅ Please enter your *full name* to book your appointment.")
        appointments[phone_number] = {"status": "awaiting_name"}

    # Step 3: Save Name and ask for Phone
    elif phone_number in appointments and appointments[phone_number]["status"] == "awaiting_name":
        user_name = incoming_msg
        appointments[phone_number]["name"] = user_name
        appointments[phone_number]["status"] = "awaiting_phone"
        message.body("✅ Thanks! Now please enter your *phone number*.")

    # Step 4: Save phone number and assign token
    elif phone_number in appointments and appointments[phone_number]["status"] == "awaiting_phone":
        user_phone = incoming_msg

        # Check if phone already has a token
        existing_token = None
        for info in appointments.values():
            if info.get("phone") == user_phone:
                existing_token = info.get("token")
                break

        if existing_token:
            token_number = existing_token
        else:
            token_number = token_counter
            token_counter += 1

        appointments[phone_number]["phone"] = user_phone
        appointments[phone_number]["status"] = "confirmed"
        appointments[phone_number]["token"] = token_number

        token_msg = f"📝 Appointment Confirmed!\n\nName: {appointments[phone_number]['name']}\nPhone: {user_phone}\nToken No: {token_number}\n\nVisit to the Clinic Between 9 to 2\nThank you"
        message.body(token_msg)

    # Step 5: Catch all
    else:
        message.body("❓ I didn't understand that. Please type 'hi' to start.")

    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000) 
