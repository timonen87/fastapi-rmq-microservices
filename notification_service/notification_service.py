import smtplib, os, json
from email.message import EmailMessage
from dotenv import load_dotenv
from email.mime.text import MIMEText


load_dotenv()


def send_notification_email(message):
    try:
        message = json.loads(message)
        receiver_email = message["email"]
        subject = message["subject"]
        body = message["body"]

        smtp_user = os.environ.get("SMTP_USER")
        smtp_password = os.environ.get("SMTP_PASSWORD")
        smtp_host = os.environ.get("SMTP_HOST")
        smtp_port = os.environ.get("SMTP_PORT")

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)

        msg_content = MIMEText(body)
        msg_content["Subject"] = subject
        msg_content["From"] = smtp_user
        msg_content["To"] = receiver_email

        server.sendmail(smtp_user, receiver_email, msg_content.as_string())
        server.quit()

        print("Письмо отправлено")
    except Exception as e:
        print(f"Ошибка отправки письма: {e}")
