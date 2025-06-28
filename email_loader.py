
import os
import mimetypes
import magic
import re
import html2text


class Email_loader():

    def get_mime_type(self, mime_type, filename, binary_data):

        try:
            detected_type = magic.from_buffer(binary_data, mime=True)
            if detected_type:
                return detected_type
        except Exception:
            pass  # Ignore magic failures silently

        if mime_type:
            return mime_type

        # Guess file extension and type
        guessed_type, _ = mimetypes.guess_type(filename)
        if guessed_type:
            return guessed_type

        return "application/octet-stream"


    def get_file_extension(self, filename):

        return os.path.splitext(filename)[-1].lower()


    def html_to_text(self, html_text):

        try:

            h = html2text.HTML2Text()

            h.ignore_links = True           # Do not include hyperlinks
            h.ignore_images = True          # Skip image tags
            h.body_width = 0                # Do not wrap text
            h.ignore_emphasis = True        # Remove **bold** and _italics_
            h.skip_internal_links = True    # Avoid internal anchors
            h.ignore_tables = True          # Do not include tables
            h.protect_links = True

            text = h.handle(html_text)

            # Remove invisible or formatting Unicode characters
            text = re.sub(r"[\u200c\u200d\u200e\u200f\u202a-\u202e\u2060-\u206f\u00ad\xa0]", " ", text)

            # Replace multiple consecutive spaces or tabs with a single space
            text = re.sub(r"[ \t]+", " ", text)

            # Normalize newlines (remove lines that are empty or have only whitespace)
            text = re.sub(r"\n\s*\n+", "\n\n", text)

            return True, text.strip()

        except Exception as E:

            return False, f"Error in parsing html: {str(E)}"
