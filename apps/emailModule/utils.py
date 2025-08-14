from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
import os
from imap_tools import MailBox, AND, OR

load_dotenv(override=True)

email = os.getenv('EMAIL')
password = os.getenv('EMAIL_APP_PASSWORD')

def send_email(from_email, app_password, to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(from_email, app_password)
        server.send_message(msg)

def fetch_emails(from_email, app_password, folder='INBOX', limit = 50):
    with MailBox('imap.gmail.com').login(from_email, app_password, folder) as mailbox:
        return [msg for msg in mailbox.fetch(limit=limit, reverse=True)]

def search_email_by_sender(email, app_password, sender_emails, folder='INBOX', limit=50):
    with MailBox('imap.gmail.com').login(email, app_password, folder) as mailbox:
        if isinstance(sender_emails, list):
            queries = [AND(from_=sender) for sender in sender_emails]
            query = OR(*queries)
        else:
            query = AND(from_=sender_emails)
        messages = mailbox.fetch(query, limit=limit, reverse=True)
        return [{
            'subject': msg.subject,
            'from': msg.from_,
            'to': msg.to,
            'date': msg.date,
            'body': msg.text or msg.html,
            'message-id': msg.headers.get('message-id', [''])[0]
        } for msg in messages]