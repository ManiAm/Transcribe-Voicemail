
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime
from email.utils import parseaddr

from email_loader import Email_loader


class Email_Parser(Email_loader):

    def __init__(self, msg_obj):

        super().__init__()

        self.message = msg_obj


    def parse_email(self) -> dict:

        message_id = self.message.get("Message-ID", None)
        if not message_id:
            return {}

        subject = self._decode_header_value(self.message.get("Subject", "(No Subject)"))
        sender = self._decode_header_value(self.message.get("From", "Unknown"))

        recipients_raw = self.message.get_all("To", [])

        recipients = []
        for r in recipients_raw:
            decoded = self._decode_header_value(r)
            _, email = parseaddr(decoded)
            if email:
                recipients.append(email)

        # Parse date
        date = self.message.get("Date")
        parsed_date = parsedate_to_datetime(date) if date else None

        body = self._get_body(self.message)
        attachments = self._get_attachments(self.message)

        return {
            "message_id": message_id,
            "date": parsed_date,
            "from": sender,
            "to": recipients,
            "subject": subject,
            "body": body,
            "attachments": attachments
        }


    def _decode_header_value(self, value: str) -> str:

        try:
            decoded_parts = decode_header(value)
            return str(make_header(decoded_parts))
        except Exception as e:
            print(f"[WARN] Failed to decode header: {value}\nReason: {e}")
            return value


    def _get_body(self, message) -> str:
        """ Extract plain text body from the email. """

        plain_text = ""
        html_text = ""

        if message.is_multipart():

            for part in message.walk():

                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", "")).lower()

                if "attachment" in content_disposition:
                    continue  # Skip attachments

                try:
                    payload = part.get_payload(decode=True)
                    if not payload:
                        continue

                    charset = part.get_content_charset() or "utf-8"
                    text = payload.decode(charset, errors="ignore")

                    if content_type == "text/plain":
                        plain_text += text
                    elif content_type == "text/html":
                        html_text += text

                except Exception:
                    continue
        else:

            try:
                payload = message.get_payload(decode=True)
                if payload:
                    charset = message.get_content_charset() or "utf-8"
                    text = payload.decode(charset, errors="ignore")
                    content_type = message.get_content_type()
                    if content_type == "text/plain":
                        plain_text = text
                    elif content_type == "text/html":
                        html_text = text
            except Exception:
                pass

        if html_text:
            status, output = self.html_to_text(html_text)
            if status and output:
                plain_text = output

        return plain_text.replace('\x00', '').strip()


    def _get_attachments(self, message) -> dict:

        attachments = {}

        if not message.is_multipart():
            return attachments

        for part in message.walk():

            content_disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in content_disposition:

                filename = part.get_filename()
                if not filename:
                    continue

                try:
                    binary_data = part.get_payload(decode=True) or b""
                    mime_type = part.get_content_type()
                    effective_mime = self.get_mime_type(mime_type, filename, binary_data)
                    attachments[filename] = {
                        "mime_type": effective_mime,
                        "extension": self.get_file_extension(filename),
                        "size": len(binary_data),
                        "data": binary_data,
                    }
                except Exception:
                    continue

        return attachments


    def update_email(self, body_new):

        # Modify the text/plain part in place
        for part in self.message.walk():
            if part.get_content_type() == "text/plain":
                part.set_payload(body_new)
                break
