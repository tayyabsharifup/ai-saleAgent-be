
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv(override=True)
email = os.getenv('EMAIL')
to_email = os.getenv('TO_EMAIL')

# password = os.getenv('EMAIL_PASSWORD')
password = os.getenv('EMAIL_APP_PASSWORD')

msg = MIMEText("Test email from Python")
msg['Subject'] = "Test"
msg['From'] = email
msg['To'] = to_email

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(email, password)  # Use App Password here
server.send_message(msg)
server.quit()
