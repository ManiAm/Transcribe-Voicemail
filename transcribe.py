
import os
import sys
import tempfile

import config
from speech_to_text_api import STT_REST_API_Client


stt_client = STT_REST_API_Client(url=config.speech_to_text_url)
if not stt_client.check_health():
    print("SST service is not reachable")
    sys.exit(1)

status, output = stt_client.load_model("openai_whisper", "small.en")
if not status:
    print(f"Cannot load openai_whisper model: {output}")
    sys.exit(1)
print(f"{output['message']}")


def transcribe_audio(attachment_dict):

    transcribed_txt = ""
    temp_file = None

    for name, details in attachment_dict.items():

        mime_type = details.get("mime_type")
        if mime_type not in ["audio/wav", "audio/x-wav"]:
            print(f"Unexpected attachment type: {mime_type}: {name}")
            continue

        data_binary = details.get("data")
        if not data_binary:
            print(f"No data found in attachment: {name}")
            continue

        try:

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file.write(data_binary)
            temp_file.close()

            print("Sending audio to backend for transcription...")

            status, output = stt_client.transcribe_file(temp_file.name, "openai_whisper", "small.en")
            if not status:
                print(f"Transcription error: {output}")
                continue

            transcript = output.get("transcript", "").strip()

            if transcript:
                transcribed_txt += transcript + "\n"
            else:
                print("No transcript returned.")

        except Exception as e:
            print(f"Transcription error: {e}")

        finally:

            if temp_file and os.path.exists(temp_file.name):
                os.remove(temp_file.name)

    return transcribed_txt.strip()
