# app.py
from flask import Flask, request
from flask import jsonify

app = Flask(__name__)

# Store appointments in memory (will reset when app restarts)
appointments = {}

@app.route('/', methods=['GET'])
def home():
    return "Bot is running"

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    user_number = request.form.get('From', '')
    user_msg = request.form.get('Body', '').strip().lower()

    # Remove 'whatsapp:' prefix
    user_number = user_number.replace("whatsapp:", "")

    if user_number in appointments:
        return respond("Appointment already booked with this number. Please visit the clinic.")

    if user_msg in ['hi', 'hello', 'book', 'appointment']:
        # Ask for name (you can expand this)
        appointments[user_number] = True  # Mark as booked
        return respond(
            "✅ Appointment booked!\n\nWhat would you like to do next?\n1. Talk to Doctor\n2. Book Another Appointment"
        )
    
    return respond("Welcome to the Clinic Bot! Type 'book' to book an appointment.")

def respond(message):
    return f"""
    <Response>
        <Message>{message}</Message>
    </Response>
    """

if __name__ == '__main__':
    app.run()
