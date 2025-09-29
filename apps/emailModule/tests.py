import imaplib
import email
import os
from getpass import getpass

IMAP_HOST = "imap-mail.outlook.com"
IMAP_PORT = 993

def get_credentials():
    email_user = os.getenv("OUTLOOK_EMAIL") or input("Outlook email: ").strip()
    app_pass = os.getenv("OUTLOOK_APP_PASS") or getpass("App password: ")
    return email_user, app_pass

def fetch_one_email(user, password):
    with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as imap:
        imap.login(user, password)
        imap.select("INBOX")
        typ, data = imap.search(None, "ALL")
        if typ != "OK" or not data[0]:
            print("No messages found.")
            return
        # Get the most recent email
        latest_id = data[0].split()[-1]
        typ, msg_data = imap.fetch(latest_id, "(RFC822)")
        if typ != "OK":
            print("Failed to fetch email.")
            return
        raw_msg = msg_data[0][1]
        msg = email.message_from_bytes(raw_msg)
        print("From:", msg["From"])
        print("Subject:", msg["Subject"])
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    print("Body:\n", part.get_payload(decode=True).decode(errors="ignore"))
                    break
        else:
            print("Body:\n", msg.get_payload(decode=True).decode(errors="ignore"))
        imap.logout()

if __name__ == "__main__":
    user, pwd = get_credentials()
    fetch_one_email(user, pwd)
