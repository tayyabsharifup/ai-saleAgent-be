
import os
import requests
from dotenv import load_dotenv
load_dotenv(override=True)

MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_API_KEY = os.getenv("MAILGUN_API")  

def send_simple_message(fromEmail, toEmail):
    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    return requests.post(
        url=url,
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": fromEmail,
            "to": toEmail,
            "subject": "Hello Dawood Siddique",
            "text": "Congratulations Dawood Siddique, THis bob email from alias"
        })

# response = send_simple_message()
# print(f'Response: {response.status_code}')
# print(f'Data: {response.json()}')