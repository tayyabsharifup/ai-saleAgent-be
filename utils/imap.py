import imaplib
import email
from dotenv import load_dotenv
import os

load_dotenv(override=True)

email = os.getenv('EMAIL')
# password = os.getenv('EMAIL_PASSWORD')
password = os.getenv('EMAIL_APP_PASSWORD')
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(email, password)  
mail.select("inbox")

status, messages = mail.search(None, 'ALL')
for num in messages[0].split():
    status, data = mail.fetch(num, '(RFC822)')
    print(f"status: {status}, data: {data}")
    # msg = email.message_from_bytes(data[0][1])
    # print("Subject:", msg["subject"])
    break
mail.logout()
