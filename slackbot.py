import os
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from flask import Flask, request
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize the Slack client
client = WebClient(token=os.environ['SLACK_API_TOKEN'])

# Create a Flask app
app = Flask(__name__)

# Initialize the signature verifier
signing_secret = os.environ['SLACK_SIGNING_SECRET']
signature_verifier = SignatureVerifier(signing_secret)

# Route for handling the Slack event verification and event handling
@app.route('/slack/events', methods=['POST'])
def slack_events():
    if not signature_verifier.is_valid_request(request.data, request.headers):
        return "Unauthorized", 401

    data = request.get_json()

    if 'event' in data and 'thread_ts' in data['event']:
        thread_ts = data['event']['thread_ts']
        channel = data['event']['channel']
        last_reply_ts = data['event']['latest_reply']

        if time.time() - float(last_reply_ts) > 1800:
            send_reminder(channel, thread_ts)
        elif last_reply_ts == '0':
            send_confirmation(channel, thread_ts)

    return 'ok'

# Function to send a confirmation reply
def send_confirmation(channel, thread_ts):
    try:
        response = client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text="Sure! We are checking this."
        )
        print("Confirmation message sent successfully!")
    except SlackApiError as e:
        print(f"Error sending confirmation message: {e.response['error']}")

# Function to send a reminder message
def send_reminder(channel, thread_ts):
    try:
        response = client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text="It's been 30 minutes. Is there a follow-up? Please provide an update."
        )
        print("Reminder message sent successfully!")
    except SlackApiError as e:
        print(f"Error sending reminder message: {e.response['error']}")

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5000)