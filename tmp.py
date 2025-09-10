import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env file
load_dotenv(override=True)

# Get Twilio credentials from environment variables
sid = os.getenv("TWILIO_ACCOUNT_SID")
token = os.getenv("TWILIO_AUTH_TOKEN")

# Initialize the Twilio client
client = Client(sid, token)

def get_child_calls(parent_call_sid):
    """
    Fetches and prints child calls for a given parent CallSid.
    """
    try:
        child_calls = client.calls.list(parent_call_sid=parent_call_sid)
        if child_calls:
            print(f"Found {len(child_calls)} child call(s):")
            for call in child_calls:
                print(f"  - SID: {call.sid}, From: {call._from}, To: {call.to}, Status: {call.status}")
        else:
            print("No child calls found for the given parent CallSid.")
        return child_calls
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    # Replace with a real parent CallSid to test
    sid = 'CA022ae7ff54bc9c5723864dd924a2cff9'
    get_child_calls(sid)