from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

token_counter = 1
appointments = {}  # patient_phone -> list of bookings
session = {}       # phone_number -> current state

@app.route("/bot", methods=["POST"])
def bot():
    global token_counter

    incoming_msg = request.values.get("Body", "").strip()
    phone_number = request.values.get("From", "")
    response = MessagingResponse()
    message = response.message()

    if phone_number not in session:
        session[phone_number] = {"step": "language"}
        message.body("🌐 Please choose your language / कृपया अपनी भाषा चुनें:\n1. English\n2. हिंदी")
        return str(response)

    user = session[phone_number]

    # Step 1: Choose Language
    if user["step"] == "language":
        if incoming_msg == "1":
            user["lang"] = "en"
            user["step"] = "menu"
            message.body("✅ Language set to English.\n\nChoose an option:\n1. Book Appointment\n2. Talk to Doctor")
        elif incoming_msg == "2":
            user["lang"] = "hi"
            user["step"] = "menu"
            message.body("✅ भाषा हिंदी में सेट की गई है।\n\nएक विकल्प चुनें:\n1. अपॉइंटमेंट बुक करें\n2. डॉक्टर से बात करें")
        else:
            message.body("❗ Invalid / अमान्य विकल्प\n1. English\n2. हिंदी")
        return str(response)

    # Step 2: Menu Options
    if user["step"] == "menu":
        if incoming_msg == "1":
            user["step"] = "awaiting_name"
            if user["lang"] == "en":
                message.body("👤 Please enter the *patient's full name*:")
            else:
                message.body("👤 कृपया मरीज का *पूरा नाम* दर्ज करें:")
        elif incoming_msg == "2":
            if user["lang"] == "en":
                message.body("📞 Please call the clinic at +91-XXXXXXXXXX to talk to the doctor.")
            else:
                message.body("📞 डॉक्टर से बात करने के लिए कृपया क्लिनिक के इस नंबर पर कॉल करें: +91-XXXXXXXXXX")
        else:
            message.body("❗ Please choose 1 or 2.\nकृपया 1 या 2 चुनें।")
        return str(response)

    # Step 3: Enter Name
    if user["step"] == "awaiting_name":
        user["name"] = incoming_msg
        user["step"] = "awaiting_patient_phone"
        if user["lang"] == "en":
            message.body("📱 Please enter the *patient's mobile number*:")
        else:
            message.body("📱 कृपया मरीज का *मोबाइल नंबर* दर्ज करें:")
        return str(response)

    # Step 4: Enter Phone → Confirm Booking
    if user["step"] == "awaiting_patient_phone":
        patient_phone = incoming_msg
        name = user["name"]

        existing = None
        for appt in appointments.get(patient_phone, []):
            if appt["name"].lower() == name.lower():
                existing = appt
                break

        if existing:
            token = existing["token"]
        else:
            token = token_counter
            token_counter += 1
            appointments.setdefault(patient_phone, []).append({"name": name, "token": token})

        if user["lang"] == "en":
            confirm = f"📝 Appointment Confirmed!\n\nName: {name}\nPhone: {patient_phone}\nToken No: {token}\n\n🏥 Visit clinic between 9 AM to 2 PM\n🙏 Thank you!\n\nReply:\n1. Book Another Appointment\n2. Main Menu"
        else:
            confirm = f"📝 अपॉइंटमेंट कन्फर्म हो गया है!\n\nनाम: {name}\nफोन: {patient_phone}\nटोकन नंबर: {token}\n\n🏥 सुबह 9 से 2 बजे के बीच क्लिनिक आएं\n🙏 धन्यवाद!\n\nउत्तर दें:\n1. एक और अपॉइंटमेंट\n2. मुख्य मेनू"

        user["step"] = "post_booking"
        message.body(confirm)
        return str(response)

    # Step 5: After Booking Options
    if user["step"] == "post_booking":
        if incoming_msg == "1":
            user["step"] = "awaiting_name"
            if user["lang"] == "en":
                message.body("👤 Please enter the *patient's full name*:")
            else:
                message.body("👤 कृपया मरीज का *पूरा नाम* दर्ज करें:")
