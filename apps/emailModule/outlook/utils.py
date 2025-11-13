import os
import requests
from typing import List, Tuple, Optional
import webbrowser
import msal
from dotenv import load_dotenv

load_dotenv(override=True)

MS_GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0'


class OutlookEmail:
    def __init__(self):
        self.application_id = os.getenv("OUTLOOK_APPLICATION_ID")
        self.client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")
        self.scopes = ['User.Read', 'Mail.Read', 'Mail.Send']
        self.client = msal.ConfidentialClientApplication(
            client_id=self.application_id,
            client_credential=self.client_secret,
            authority='https://login.microsoftonline.com/consumers/'
        )

    def get_authroization_url(self):
        client = msal.ConfidentialClientApplication(
            client_id=self.application_id,
            client_credential=self.client_secret,
            authority='https://login.microsoftonline.com/consumers/'
        )
        auth_request_url = client.get_authorization_request_url(scopes=self.scopes)
        return auth_request_url
    
    def get_refresh_token(self, authorization_code: str) -> Tuple[bool, str]:
        token_response = self.client.acquire_token_by_authorization_code(
            code=authorization_code,
            scopes=self.scopes
        )

        if 'access_token' in token_response:
            if 'refresh_token' in token_response:
                return (True, token_response['refresh_token'])
        else:
            return (False, token_response['error_description'])
        

    def get_access_token(self, refresh_token: str) -> Tuple[bool, str]:

        client = msal.ConfidentialClientApplication(
            client_id=self.application_id,
            client_credential=self.client_secret,
            authority='https://login.microsoftonline.com/consumers/'
        )

        token_response = client.acquire_token_by_refresh_token(
            refresh_token, scopes=self.scopes
        )

        if 'access_token' in token_response:
            return (True, token_response['access_token'])
        else:
            return (False, token_response.get('error_description', 'Unknown error'))

    def get_outlook_all_email(self,  refresh_token: str, limit: int = 10) -> Tuple[bool, List[dict]]:
        access_token = self.get_access_token(refresh_token)
        if not access_token[0]:
            return (False, access_token[1])
        access_token_str = access_token[1]
        endpoint = f"{MS_GRAPH_BASE_URL}/me/mailFolders/inbox/messages"
        endpoint = f"{MS_GRAPH_BASE_URL}/me/messages"

        headers = {
            'Authorization': f'Bearer {access_token_str}'
        }
        try:
            return_response = []
            params = {
                '$top': limit,
                '$orderby': 'receivedDateTime DESC',
            }
            response = requests.get(endpoint, headers=headers, params=params)
            if response.status_code != 200:
                raise Exception(f'Failed to retrieve emails: {response.text}')

            json_response = response.json()
            # print(json_response)
            for mail in json_response.get('value', []):
                subject = mail.get("subject", "")
                from_email = mail.get("from", {}).get(
                    "emailAddress", {}).get("address", "")

                # Handle cases with no recipients
                to_recipients = mail.get("toRecipients", [])
                to_email = ""
                if to_recipients:
                    to_email = to_recipients[0].get(
                        "emailAddress", {}).get("address", "")

                received = mail.get("receivedDateTime", "")
                body = mail.get("body", {}).get("content", "")
                id = mail.get('id')

                if from_email is None or from_email == '':
                    continue

                if not id:
                    continue

                mail_dict = {
                    'subject': subject,
                    'from': from_email,
                    'to': to_email,
                    'received': received,
                    'body': body,
                    'message-id': mail.get('id'),
                }
                return_response.append(mail_dict)
            return (True, return_response)
        except Exception as e:
            return (False, str(e))

    def send_outlook_email(self, refresh_token: str, to_email: str, subject: str, body: str) -> Tuple[bool, str]:
        access_token = self.get_access_token(refresh_token)
        if not access_token[0]:
            return (False, access_token[1])
        access_token_str = access_token[1]

        message = {
            'subject': subject,
            'body': {
                'contentType': 'Text',
                'content': body
            },
            'toRecipients': [
                {
                    'emailAddress': {
                        'address': to_email
                    }
                }
            ]
        }

        endpoint = f"{MS_GRAPH_BASE_URL}/me/sendMail"
        headers = {
            'Authorization': f'Bearer {access_token_str}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                endpoint, headers=headers, json={'message': message})
            if response.status_code != 202:
                return (False, f'Failed to send email: {response.text}')
            return (True, 'Email sent successfully')
        except Exception as e:
            return (False, str(e))

    def search_outlook_email(self, refresh_token: str, from_email: str, limit: int = 10) -> Tuple[bool, List[dict]]:
        access_token = self.get_access_token(refresh_token)
        if not access_token[0]:
            return (False, access_token[1])
        access_token_str = access_token[1]
        endpoint = f"{MS_GRAPH_BASE_URL}/me/mailFolders/inbox/messages?$filter=from/emailAddress/address eq '{from_email}'"
        endpoint = f"{MS_GRAPH_BASE_URL}/me/messages?$filter=from/emailAddress/address eq '{from_email}'"
        headers = {
            'Authorization': f'Bearer {access_token_str}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(endpoint, headers=headers)
            if response.status_code != 200:
                return (False, f'Failed to search emails: {response.text}')

            emails = response.json().get('value', [])
            result = []
            for email in emails:
                result.append({
                    'subject': email.get('subject', ''),
                    'from': (
                        email.get('from', {})
                        .get('emailAddress', {})
                        .get('address', '')
                    ),
                    'to': (
                        email.get('toRecipients', [{}])[0].get(
                            'emailAddress', {}).get('address', '')
                    ),
                    'received': email.get('receivedDateTime', ''),
                    'body': email.get('body', {}).get('content', ''),
                    'message-id': email.get('id', '')
                })

            return (True, result)
        except Exception as e:
            return (False, str(e))



if __name__ == "__main__":
    application_id = os.getenv("OUTLOOK_APPLICATION_ID")
    client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")
    scopes = ['User.Read', 'Mail.Read', 'Mail.Send']

    try:
        refresh_token = 'M.C558_SN1.0.U.-Cm6QwchB2eulv0d6pF4KxNRSGX16t0oG2NxvGfU17GI0Uv2rIR0EyibFAmI80fc1CGJf9lnSoCcEiQSVDhgCOS9wDE2zBmaESmoWXtywY6j0HSCwQ!*PAO4e6D2XYFbFkqblYMXreSPs!ughDPM5yJh5OE91usBw51Qgq!4Xkh9trlikXdZ9xZ5KNuW6fy!9VsM447ybGr3L2gmvn33FwcLip31zOJa3pBn3*ZHPg8ea!gHXoOPl5BwxyNCOCW6IVeOjQLIdB3*FeNMxzcymUeburra2kcm4iIBgOcyF35U2ZRKSXbp6gVaB7qhHZljvRorZboTi8i8YBW7YOYO2WhLD3btuOu2M8YcARN45wfarzw9OiygfVb7MRhHMWEYXX7UeJtreMhNzSwkYlqz6KzI$'
        umar33_refresh_token = 'M.C560_BAY.0.U.-CgfjhxrdDrhB*6DFgKtKPuaj0AEpoJp2zkeRq6ck*CutUuUM6HHFamZ9jvc5IIHP1za1XSuW8Ljxwrrj!ifa7ACLsQlbDN*4rpyclMbNkhn5t*nSND1viaWRfag*i5g7LqBGnRZLaxuF4w*PHyE01ycGBO494TYq*yWHezwZ3l*7Iy1Jro7Ljod5SThcevpJRehn0ZnIzN2E92tsxfzl3kvSc8PpzmPvHqcXgngysfMpnF*BqHrvkb9hIIMlofLtqfqrpudqXuwrYaXwEAh03k80!wTZAkR41aqJ3GX9gfxac!gWaNactRpA4YSKIOn0*JleJ1iivapS07vV2xhnYVM7aIbnPOu!Llfqn09CNNmzz*6q2mngM8cGI5LTYmTQpA$$'
        refresh_token = umar33_refresh_token
        outlook = OutlookEmail()
        emails = outlook.search_outlook_email(refresh_token=refresh_token, from_email='davidbacken@proton.me')
        print(emails)
        # emails = outlook.get_outlook_all_email(refresh_token=refresh_token)
        # print(emails)
        # is_send, message =outlook.send_outlook_email(refresh_token, 'dawoodsiddique469@gmail.com', 'test', 'test')
        # print(is_send, message)
    except Exception as e:
        print("Error:", e)
        exit(1)
