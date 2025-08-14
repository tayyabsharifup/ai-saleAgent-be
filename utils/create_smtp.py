
import os
import requests
from requests.auth import HTTPBasicAuth
from send_email import send_simple_message

MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")      # e.g. your-domain.com
MAILGUN_API_KEY = os.getenv("MAILGUN_API")    # your Mailgun private API key

def create_smtp_user(login: str, password: str = None):

    url = f"https://api.mailgun.net/v3/domains/{MAILGUN_DOMAIN}/credentials"
    data = {
        "login": login,
        "password": password
        }
    resp = requests.get(url, auth=('api', MAILGUN_API_KEY)) 
    resp_data = resp.json()['items']
    mail_exist = False
    for dt in resp_data:
        
        mail = dt['mailbox']
        if login == mail:
            # Email already exsits
            mail_exist = True
    if not mail_exist:
        resp = requests.post(
            url,
            auth=("api", MAILGUN_API_KEY),
            data=data,
        )
        print(f"Mail creation response: {resp.json()}")
        print(f"mail status: {resp.status_code}")
        resp.raise_for_status()
    
    # send mail
    mail_send_response = send_simple_message(f"{login}@{MAILGUN_DOMAIN}", 'dawoodsiddique469@gmail.com')
    if mail_send_response.status_code == 200:
        print("Mail Sent")
    
    print(f"mail response: {mail_send_response.json()}")
    print(f"mail status code: {mail_send_response.status_code}")


    return resp.json()

if __name__ == "__main__":
    result = create_smtp_user("FurqanAI", "PakPassword321")
    # print(result)
