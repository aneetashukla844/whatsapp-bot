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

    # Check if this number already booked
    if phone_number in appointments and appointments[phone_number]["status"] == "confirmed":
        token_number = appointments[phone_number]["token"]
        user_name = appointments[phone_number]["name"]
        user_phone = appointments[phone_number]["phone"]
        token_msg = f"📝 Appointment Already Confirmed!\n\nName: {user_name}\nPhone: {user_phone}\nToken No: {token_number}\n\nVisit to the clinic between 9 to 2\nThank you"
        message.body(token_msg)
        return str(response)

    # Step 1: Ask for Name
    if phone_number not in appointments or appointments[phone_number]["status"] == "start":
        appointments[phone_number] = {"status": "awaiting_name"}
        message.body("✅ Welcome to DB Shukla's Clinic!\nPlease enter your *full name* to book an appointment.")
        return str(response)

    # Step 2: Save Name and ask for Phone
    if appointments[phone_number]["status"] == "awaiting_name":
        user_name = incoming_msg
        appointments[phone_number]["name"] = user_name
        appointments[phone_number]["status"] = "awaiting_phone"
        message.body("✅ Thanks! Now please enter your *phone number*.")
        return str(response)

    # Step 3: Save phone number and assign token
    if appointments[phone_number]["status"] == "awaiting_phone":
        user_phone = incoming_msg

        # Check if this phone number already has a token
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

        token_msg = f"📝 Appointment Confirmed!\n\nName: {appointments[phone_number]['name']}\nPhone: {user_phone}\nToken No: {token_number}\n\nVisit to the clinic between 9 to 2\nThank you"
        message.body(token_msg)
        return str(response)

    # Catch-all fallback
    message.body("❓ Something went wrong. Please try again.")
    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
