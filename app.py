import os
import json
from datetime import datetime
from flask import Flask, request, Response, jsonify, send_file
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

app = Flask(__name__)

AUTO_REPLY_MESSAGE = os.getenv(
    "AUTO_REPLY_MESSAGE",
    "Sorry we missed your call! Book here: https://yourbookinglink.com"
)

TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

LOG_FILE = "logs/twilio_events.log"


def log_event(event):
    os.makedirs("logs", exist_ok=True)
    event["logged_at"] = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")


@app.get("/")
def health_check():
    return jsonify({
        "status": "ok",
        "service": "twilio-missed-call-auto-text",
        "test_mode": TEST_MODE
    })


@app.route("/twilio/webhook", methods=["POST"])
def twilio_webhook():
    from_number = request.form.get("From")
    to_number = request.form.get("To")
    call_status = request.form.get("CallStatus")
    direction = request.form.get("Direction")
    call_sid = request.form.get("CallSid")

    log_event({
        "type": "incoming_call_webhook",
        "from": from_number,
        "to": to_number,
        "call_status": call_status,
        "direction": direction,
        "call_sid": call_sid
    })

    if not from_number:
        return Response("Missing From number", status=400, mimetype="text/plain")

    if TEST_MODE:
        log_event({
            "type": "test_mode_sms_skipped",
            "to": from_number,
            "body": AUTO_REPLY_MESSAGE
        })
        return Response("OK - TEST MODE", mimetype="text/plain")

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        body=AUTO_REPLY_MESSAGE,
        from_=TWILIO_PHONE_NUMBER,
        to=from_number
    )

    log_event({
        "type": "sms_sent",
        "to": from_number,
        "message_sid": message.sid
    })

    return Response("OK", mimetype="text/plain")


@app.get("/logs")
def view_logs():
    if not os.path.exists(LOG_FILE):
        return jsonify([])

    events = []
    with open(LOG_FILE, "r") as f:
        for line in f.readlines()[-50:]:
            try:
                events.append(json.loads(line))
            except:
                continue

    return jsonify(events)


@app.get("/demo")
def demo_page():
    return send_file("demo.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
