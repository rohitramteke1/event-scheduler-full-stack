import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from email.header import Header

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM")

# print(
# "EMAIL_HOST", EMAIL_HOST, '\n'
# "EMAIL_PORT", EMAIL_PORT, '\n'
# "EMAIL_USER", EMAIL_USER, '\n'
# "EMAIL_PASS", EMAIL_PASS, '\n'
# "EMAIL_FROM", EMAIL_FROM, '\n'
# )

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = Header(subject, "utf-8")

    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"📨 Email sent to {to_email}")
    except Exception as e:
        print("❌ Email send failed:", e)
