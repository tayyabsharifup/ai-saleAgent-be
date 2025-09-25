from dotenv import load_dotenv
import os

load_dotenv(override=True)

# Create your tests here.
email = os.getenv('OUTLOOK')
password = os.getenv('OUTLOOK_PASSWORD')

from imap_tools import MailBox, AND, OR
with MailBox('outlook.office365.com').login(email,password,'INBOX') as mailbox:
    print( [msg for msg in mailbox.fetch(reverse=True)])