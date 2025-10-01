import os
import requests
from typing import List
import webbrowser
import msal
from dotenv import load_dotenv

load_dotenv(override=True)

MS_GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0'


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
        response = requests.post(endpoint, headers=headers, json={'message': message})
        if response.status_code != 202:
            raise Exception(f'Failed to send email: {response.text}')
        print('Email sent successfully.')
    except Exception as e:
        print('error', str(e))




if __name__ == "__main__":
    application_id = os.getenv("OUTLOOK_APPLICATION_ID")
    client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")
    scopes = ['User.Read', 'Mail.Read', 'Mail.Send']

    try:
        access_token = get_access_token(application_id, client_secret, scopes)
        print("Access Token:", access_token)
        get_all_email(access_token)
        send_email(access_token, 'dawoodsiddique469@gmail.com', 'test outlook', 'test outlook')
    except Exception as e:
        print("Error:", e)
        exit(1)
