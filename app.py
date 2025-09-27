from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

token_counter = 1
appointments = {}  # phone -> info
sessions = {}      # WhatsApp sender -> current flow

@app.route("/bot", methods=["POST"])
def bot():
    global token_counter

    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    response = MessagingResponse()
    message = response.message()

    # Initialize session if not exists
    if sender not in sessions:
        sessions[sender] = {"step": "ask_name"}

    step = sessions[sender]["step"]

    # Step 1: Ask patient name
    if step == "ask_name":
        sessions[sender]["step"] = "ask_phone"
        sessions[sender]["patient_name"] = incoming_msg
        message.body("✅ Please enter the patient’s phone number.")
        return str(response)

    # Step 2: Ask patient phone
    if step == "ask_phone":
        patient_phone = incoming_msg

        # Check if already booked
        for info in appointments.values():
            if info.get("phone") == patient_phone:
                message.body(f"📝 Appointment already booked!\nVisit to the clinic between 9 to 2\nThank you")
                sessions[sender]["step"] = "finished"
                return str(response)

        # New appointment
        patient_name = sessions[sender]["patient_name"]
        token_number = token_counter
        token_counter += 1

        appointments[sender] = {
            "name": patient_name,
            "phone": patient_phone,
            "token": token_number
        }

        sessions[sender]["step"] = "options"

        message.body(f"📝 Appointment Confirmed!\n\nName: {patient_name}\nPhone: {patient_phone}\nToken No: {token_number}\n\nPlease choose an option:\n1. Book another appointment\n2. Talk to doctor\n3. Exit")
        return str(response)

    # Step 3: Handle options after booking
    if step == "options":
        if incoming_msg == "1":
            sessions[sender]["step"] = "ask_name"
            message.body("✅ Enter the name of the patient for the new appointment.")
        elif incoming_msg == "2":
            message.body("📞 You can contact Dr. Sharma at +91-9876543210")
        elif incoming_msg == "3":
            patient_info = appointments.get(sender, {})
            message.body(f"Thank you! Visit to the clinic between 9 to 2\nPatient: {patient_info.get('name', '')}")
            sessions[sender]["step"] = "finished"
        else:
            message.body("❓ Invalid option. Please choose:\n1. Book another appointment\n2. Talk to doctor\n3. Exit")
        return str(response)

    # Step 4: Finished or fallback
    message.body("❓ Something went wrong. Please start again.")
    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
