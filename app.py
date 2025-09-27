from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Twilio account (replace with your real credentials)
ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Your Twilio Sandbox number

client = Client(ACCOUNT_SID, AUTH_TOKEN)

token_counter = 1
appointments = {}  # mobile -> info
sessions = {}      # sender -> session data

# Message templates
MESSAGES = {
    "en": {
        "ask_book": "Do you want to book an appointment? Please choose:",
        "ask_name": "✅ Please enter the patient's full name:",
        "ask_mobile": "✅ Please enter the patient's mobile number:",
        "ask_address": "✅ Please choose the patient's address:",
        "ask_other_address": "Please type the patient's address:",
        "confirm": "📝 Appointment Confirmed!\n\nName: {name}\nPhone: {phone}\nAddress: {address}\nToken No: {token}\n\nVisit the clinic between 9 to 2\nThank you",
        "already_booked": "📝 Appointment already booked!\nVisit the clinic between 9 to 2\nThank you",
        "post_options": "Please choose an option:\n1. Book another appointment\n2. Talk to doctor\n3. Exit",
        "invalid_option": "❓ Invalid option. Please choose 1, 2, or 3.",
        "talk_doctor": "📞 You can contact Dr. Sharma at +91-9876543210",
        "thank_you": "👍 Thank you! Visit the clinic between 9 to 2"
    },
    "hi": {
        "ask_book": "क्या आप अपॉइंटमेंट बुक करना चाहते हैं? कृपया चुनें:",
        "ask_name": "✅ कृपया मरीज का पूरा नाम दर्ज करें:",
        "ask_mobile": "✅ कृपया मरीज का मोबाइल नंबर दर्ज करें:",
        "ask_address": "✅ कृपया मरीज का पता चुनें:",
        "ask_other_address": "कृपया मरीज का पता टाइप करें:",
        "confirm": "📝 अपॉइंटमेंट कन्फर्म हो गया!\n\nनाम: {name}\nफोन: {phone}\nपता: {address}\nटोकन नंबर: {token}\n\nकृपया 9 से 2 बजे के बीच क्लिनिक में आएँ\nधन्यवाद",
        "already_booked": "📝 अपॉइंटमेंट पहले से बुक है!\nकृपया 9 से 2 बजे के बीच क्लिनिक में आएँ\nधन्यवाद",
        "post_options": "कृपया विकल्प चुनें:\n1. दूसरा अपॉइंटमेंट बुक करें\n2. डॉक्टर से बात करें\n3. बाहर निकलें",
        "invalid_option": "❓ अमान्य विकल्प। कृपया 1, 2, या 3 चुनें।",
        "talk_doctor": "📞 आप डॉ. शर्मा से +91-9876543210 पर संपर्क कर सकते हैं",
        "thank_you": "👍 धन्यवाद! कृपया 9 से 2 बजे के बीच क्लिनिक में आएँ"
    }
}

@app.route("/bot", methods=["POST"])
def bot():
    global token_counter

    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    response = MessagingResponse()
    message = response.message()

    # Initialize session
    if sender not in sessions:
        sessions[sender] = {
            "step": "choose_language",
            "lang": "en"
        }
        # Ask language selection
        message.body("Please select language / कृपया भाषा चुनें:\n1. English\n2. हिन्दी")
        return str(response)

    session = sessions[sender]
    step = session["step"]
    lang = session["lang"]

    # Step: Language selection
    if step == "choose_language":
        if incoming_msg == "1":
            session["lang"] = "en"
            lang = "en"
        elif incoming_msg == "2":
            session["lang"] = "hi"
            lang = "hi"
        else:
            message.body("Please choose / कृपया 1 या 2 चुनें")
            return str(response)
        session["step"] = "ask_book"
        message.body(MESSAGES[lang]["ask_book"])
        return str(response)

    # Step: Ask to book
    if step == "ask_book":
        if incoming_msg.lower() in ["yes", "हाँ", "ha", "haam"]:
            session["step"] = "ask_name"
            message.body(MESSAGES[lang]["ask_name"])
        elif incoming_msg.lower() in ["no", "नहीं", "nahin"]:
            message.body(MESSAGES[lang]["thank_you"])
            session["step"] = "finished"
        else:
            message.body(MESSAGES[lang]["ask_book"])
        return str(response)

    # Step: Ask Name
    if step == "ask_name":
        session["name"] = incoming_msg
        session["step"] = "ask_mobile"
        message.body(MESSAGES[lang]["ask_mobile"])
        return str(response)

    # Step: Ask Mobile
    if step == "ask_mobile":
        mobile = incoming_msg
        # Check duplicate
        if mobile in appointments:
            message.body(MESSAGES[lang]["already_booked"])
            session["step"] = "finished"
            return str(response)
        session["mobile"] = mobile
        session["step"] = "ask_address"
        # Show two options: Rewa or Other
        message.body(MESSAGES[lang]["ask_address"] + "\n1. Rewa\n2. Other")
        return str(response)

    # Step: Ask Address
    if step == "ask_address":
        if incoming_msg == "1":
            address = "Rewa"
        elif incoming_msg == "2":
            session["step"] = "ask_other_address"
            message.body(MESSAGES[lang]["ask_other_address"])
            return str(response)
        else:
            message.body(MESSAGES[lang]["ask_address"] + "\n1. Rewa\n2. Other")
            return str(response)

        # Save appointment
        name = session["name"]
        mobile = session["mobile"]
        appointments[mobile] = {
            "name": name,
            "phone": mobile,
            "address": address,
            "token": token_counter
        }
        token = token_counter
        token_counter += 1
        session["step"] = "post_options"
        message.body(MESSAGES[lang]["confirm"].format(name=name, phone=mobile, address=address) + "\n\n" + MESSAGES[lang]["post_options"])
        return str(response)

    # Step: Ask Other Address
    if step == "ask_other_address":
        address = incoming_msg
        name = session["name"]
        mobile = session["mobile"]
        appointments[mobile] = {
            "name": name,
            "phone": mobile,
            "address": address,
            "token": token_counter
        }
        token = token_counter
        token_counter += 1
        session["step"] = "post_options"
        message.body(MESSAGES[lang]["confirm"].format(name=name, phone=mobile, address=address) + "\n\n" + MESSAGES[lang]["post_options"])
        return str(response)

    # Step: Post booking options
    if step == "post_options":
        if incoming_msg == "1":
            session["step"] = "ask_name"
            message.body(MESSAGES[lang]["ask_name"])
        elif incoming_msg == "2":
            message.body(MESSAGES[lang]["talk_doctor"])
        elif incoming_msg == "3":
            message.body(MESSAGES[lang]["thank_you"])
            session["step"] = "finished"
        else:
            message.body(MESSAGES[lang]["invalid_option"])
        return str(response)

    # Fallback
    message.body("❓ Something went wrong. Please restart by typing Yes or No.")
    return str(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
