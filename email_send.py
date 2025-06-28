
import io
import smtplib
from email.generator import BytesGenerator


def send_email(msg_obj, msg_from, msg_to):

    # Serialize updated message to bytes
    buffer = io.BytesIO()
    gen = BytesGenerator(buffer)
    gen.flatten(msg_obj)
    email_bytes = buffer.getvalue()

    with smtplib.SMTP("localhost") as smtp:
        smtp.sendmail(msg_from, msg_to, email_bytes)
