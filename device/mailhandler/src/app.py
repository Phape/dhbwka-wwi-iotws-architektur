import smtplib
import ssl
from socket import gaierror
import os

port = os.getenv('MAIL_PORT')
smtp_server = os.getenv('MAIL_SMTP_SERVER')
sender_email = os.getenv('MAIL_FROM')
receiver_email = os.getenv('MAIL_TO')
password = os.getenv('MAIL_PWD')
message = """\
Subject: Hallo

Diese Nachricht wurde mit Python gesendet."""

try:
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

    print("Gesendet")

except (gaierror, ConnectionRefusedError):
    print('Verbindung zum Server fehlgeschlagen. Sind alle Verbindungseinstellungen korrekt?')
except smtplib.SMTPServerDisconnected:
    print('Verbindung zum Server fehlgeschlagen. Falscher Nutzer/Passwort?')
except smtplib.SMTPException as e:
    print('SMTP Error: ' + str(e))