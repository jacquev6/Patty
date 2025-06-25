import email.mime.text
import smtplib

from . import settings


# This is purely integration code. Unit tests for this code would just be a repetition of the code, but using mocks.
# So: THIS CODE IS NOT TESTED AUTOMATICALLY.
def send_mail(to: str, subject: str, body: str) -> None:
    message = email.mime.text.MIMEText(body)
    message["Subject"] = subject
    message["From"] = settings.MAIL_SENDER
    message["To"] = to

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp_server:
        smtp_server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp_server.sendmail(settings.MAIL_SENDER, to, message.as_string())
