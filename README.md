# Twilio Missed-Call Auto Text

Flask backend for Twilio webhooks that:

- Handles incoming SMS and call webhooks at `POST /twilio/webhook`
- Replies to incoming SMS with:
  `Sorry we missed you! Book here: https://yourbookinglink.com`
- Sends the same text after an incoming call when Twilio credentials are configured
- Logs phone number, UTC timestamp, event type, Twilio SID, and message body to `logs/twilio_events.log`
- Runs on port `5000`

## Project Structure

```text
missed-call-auto-text/
  app.py
  requirements.txt
  .env.example
  .gitignore
  logs/
    .gitkeep
```

## Setup

```bash
cd missed-call-auto-text
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `python3 -m venv .venv` fails because `ensurepip` is unavailable, install Python's venv and pip packages first:

```bash
sudo apt install python3-venv python3-pip
```

For missed-call SMS sending, copy `.env.example` to `.env` and fill in your Twilio values:

```bash
cp .env.example .env
```

`TWILIO_FROM_NUMBER` must be a Twilio phone number or Messaging Service sender that can send SMS.

## Run

```bash
python app.py
```

The server starts on:

```text
http://localhost:5000
```

Health check:

```bash
curl http://localhost:5000/
```

## Configure Twilio

Twilio must be able to reach your local server. For local development, expose port `5000` with a tunnel such as ngrok:

```bash
ngrok http 5000
```

In the Twilio Console, set your phone number webhooks to:

```text
https://YOUR_PUBLIC_TUNNEL_URL/twilio/webhook
```

Use `HTTP POST` for both:

- A message comes in
- A call comes in

## Test Locally

Simulate an SMS webhook:

```bash
curl -X POST http://localhost:5000/twilio/webhook \
  -d "From=+15550001111" \
  -d "Body=Hello" \
  -d "MessageSid=SM123"
```

Simulate a call webhook:

```bash
curl -X POST http://localhost:5000/twilio/webhook \
  -d "From=+15550001111" \
  -d "CallSid=CA123"
```

View logs:

```bash
cat logs/twilio_events.log
```
