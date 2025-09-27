from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

token_counter = 1
appointments = {}  # mobile -> info
sessions = {}      # sender -> current flow

@app.route("/bot", methods=["POST"])
def bot():
    global token_counter

    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    response = MessagingResponse()
    message = response.message()

    # Initialize session
    if sender not in sessions:
        sessions[sender] = {"step": "ask_book"}

    step = sessions[sender]["step"]

    # Step 0: Ask if they want appointment
    if step == "ask_book":
        if incoming_msg.lower() == "yes":
            sessions[sender]["step"] = "ask_name"
            message.body("✅ Please enter the patient's full name:")
        elif incoming_msg.lower() == "no":
            message.body("👍 Okay! If you need anything, message anytime.")
            sessions[sender]["step"] = "finished"
        else:
            message.body("Do you want to book an appointment? Please reply Yes or No")
        return str(response)

    # Step 1: Ask Name
    if step == "ask_name":
        sessions[sender]["name"] = incoming_msg
        sessions[sender]["step"] = "ask_mobile"
        message.body("✅ Please enter the patient's mobile number:")
        return str(response)

    # Step 2: Ask Mobile
    if step == "ask_mobile":
        mobile = incoming_msg
        # Check duplicate
        if mobile in appointments:
            message.body(f"📝 Appointment already booked!\nVisit to the clinic between 9 to 2\nThank you")
            sessions[sender]["step"] = "finished"
            return str(response)
        sessions[sender]["mobile"] = mobile
        sessions[sender]["step"] = "ask_address"
        message.body("✅ Please enter the patient's address:")
        return str(response)

    # Step 3: Ask Address
    if step == "ask_address":
        address = incoming_msg
        name = sessions[sender]["name"]
        mobile = sessions[sender]["mobile"]

        # Save appointment
        appointments[mobile] = {
            "name": name,
            "phone": mobile,
            "address": address,
            "token": token_counter
        }
        token_number = token_counter
        token_counter += 1

        sessions[sender]["step"] = "options"

        message.body(f"📝 Appointment Confirmed!\n\nName: {name}\nPhone: {mobile}\nAddress: {address}\nToken No: {token_number}\n\nVisit the clinic between 9 to 2\nThank you\n\nOptions:\n1. Book another appointment\n2. Talk to doctor\n3. Exit")
        return str(response)

    # Step 4: Options after booking
    if step == "options":
        if incoming_msg == "1":
            sessions[sender]["step"] = "ask_name"
            message.body("✅ Enter the patient's full name for the new appointment:")
        elif incoming_msg == "2":
            message.body("📞 You can contact Dr. Sharma at +91-9876543210")
        elif incoming_msg == "3":
            message.body("👍 Thank you! Visit to the clinic between 9 to 2")
            sessions[sender]["step"] = "finished"
        else:
            message.body("❓ Invalid option. Please choose:\n1. Book another appointment\n2. Talk to doctor\n3. Exit")
        return str(response)

    # Fallback
    message.body("❓ Something went wrong. Please type Yes to book an appointment.")
    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
