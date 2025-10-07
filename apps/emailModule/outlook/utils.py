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
            return (False, token_response['error_description'])

    def get_outlook_all_email(self,  refresh_token: str, limit: int = 10) -> Tuple[bool, List[dict]]:
        access_token = self.get_access_token(refresh_token)
        if not access_token:
            return (False, 'Failed to get access token')
        endpoint = f"{MS_GRAPH_BASE_URL}/me/messages"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        try:
            for i in range(0, 4, 2):
                params = {
                    '$top': 2,
                    '$skip': i,
                    '$orderby': 'receivedDateTime DESC',
                    '$select': '*',
                }
            response = requests.get(endpoint, headers=headers, params=params)
            if response.status_code != 200:
                raise Exception(f'Failed to retrieve emails: {response.text}')

            json_response = response.json()

            return_response = []
            for mail in json_response.get('value', []):
                subject = mail.get("subject", "")
                from_email = mail.get("from", {}).get(
                    "emailAddress", {}).get("name", "")
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
                    'received': received,
                    'body': body,
                    'id': mail.get('id'),
                }

                return_response.append(mail_dict)
                # print(f'Subject: {mail.get("subject", "")}')
                # print(
                #     f'From: {mail.get("from", {}).get("emailAddress", {}).get("name", "")}')
                # print(f'Received: {mail.get("receivedDateTime", "")}')
                # print(f'Body: {mail.get("body", {}).get("content", "")}')
                # print('---')
            return (True, return_response)
        except Exception as e:
            return (False, str(e))


def get_access_token_from_refresh_token(refresh_token):
    application_id = os.getenv("OUTLOOK_APPLICATION_ID")
    client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")
    scopes = ['User.Read', 'Mail.Read', 'Mail.Send']

    client = msal.ConfidentialClientApplication(
        client_id=application_id,
        client_credential=client_secret,
        authority='https://login.microsoftonline.com/consumers/'
    )

    token_response = client.acquire_token_by_refresh_token(
        refresh_token, scopes=scopes
    )

    if 'access_token' in token_response:
        return True, token_response['access_token']
    else:
        return False, token_response['error_description']


def get_access_token(application_id: str, client_secret: str, scopes: List[str]) -> str:
    client = msal.ConfidentialClientApplication(
        client_id=application_id,
        client_credential=client_secret,
        authority='https://login.microsoftonline.com/consumers/'
    )

    # Check if there is a refresh token stored
    refresh_token = None
    if os.path.exists('refresh_token.txt'):
        with open('refresh_token.txt', 'r') as file:
            refresh_token = file.read().strip()

    print(f"Refresh Token: {refresh_token}")
    if refresh_token:
        # Try to acquire a new access token using the refresh token
        token_response = client.acquire_token_by_refresh_token(
            refresh_token, scopes=scopes)
        
    else:
        # No refresh token, proceed with the authorization code flow
        auth_request_url = client.get_authorization_request_url(scopes=scopes)
        webbrowser.open(auth_request_url)
        authorization_code = input(
            "Enter the authorization code from the redirect URL: ")
        if not authorization_code:
            raise ValueError("Authorization code is required.")

        token_response = client.acquire_token_by_authorization_code(
            code=authorization_code,
            scopes=scopes
        )

    if 'access_token' in token_response:
        if 'refresh_token' in token_response:
            with open('refresh_token.txt', 'w') as file:
                file.write(token_response['refresh_token'])
        return token_response['access_token']
    else:
        raise Exception(token_response['error_description'])


def get_all_email(access_token: str):
    endpoint = f"{MS_GRAPH_BASE_URL}/me/messages"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    try:
        for i in range(0, 4, 2):
            params = {
                '$top': 2,
                '$skip': i,
                '$orderby': 'receivedDateTime DESC',
                '$select': '*',
            }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f'Failed to retrieve emails: {response.text}')

        json_response = response.json()

        for mail in json_response.get('value', []):
            print(f'Subject: {mail.get("subject", "")}')
            print(
                f'From: {mail.get("from", {}).get("emailAddress", {}).get("name", "")}')
            print(f'Received: {mail.get("receivedDateTime", "")}')
            print(f'Body: {mail.get("body", {}).get("content", "")}')
            print(f'Id: {mail.get("id", "")}')
            print('---')
        return json_response
    except Exception as e:
        print('error', str(e))


def send_email(access_token: str, to_email: str, subject: str, body: str):
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
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            endpoint, headers=headers, json={'message': message})
        if response.status_code != 202:
            raise Exception(f'Failed to send email: {response.text}')
        print(f'Email sent successfully. status code {response.status_code}')
    except Exception as e:
        print('error', str(e))


if __name__ == "__main__":
    application_id = os.getenv("OUTLOOK_APPLICATION_ID")
    client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")
    scopes = ['User.Read', 'Mail.Read', 'Mail.Send']

    try:
        access_token = get_access_token(application_id, client_secret, scopes)
        print("Access Token:", access_token)
        print(get_all_email(access_token))
        # send_email(access_token, 'dawoodsiddique496@gmail.com',
        #            'test outlook', 'test outlook')
    except Exception as e:
        print("Error:", e)
        exit(1)
