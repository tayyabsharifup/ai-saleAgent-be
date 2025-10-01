import os
import webbrowser
import msal
from dotenv import load_dotenv

load_dotenv(override=True)

MS_GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0'

def get_access_token(application_id, client_secret, scopes):
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
        token_response = client.acquire_token_by_refresh_token(refresh_token, scopes=scopes)
    else:
        # No refresh token, proceed with the authorization code flow
        auth_request_url = client.get_authorization_request_url(scopes=scopes)
        webbrowser.open(auth_request_url)
        authorization_code = input("Enter the authorization code from the redirect URL: ")
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

if __name__ == "__main__":
    application_id = os.getenv("OUTLOOK_APPLICATION_ID")
    client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")
    scopes = ['User.Read', 'Mail.Read', 'Mail.Send']

    try:
        access_token = get_access_token(application_id, client_secret, scopes)
        print("Access Token:", access_token)
    except Exception as e:
        print("Error:", e)
        exit(1)

