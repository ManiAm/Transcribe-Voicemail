
import os
import uvicorn
import logging
from datetime import datetime
from email import message_from_string

from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

from email_parser import Email_Parser
from transcribe import transcribe_audio
from email_send import send_email


logging.getLogger("httpx").setLevel(logging.WARNING)

app = FastAPI(
    title="Transcribe-Voicemail",
    description="voicemail transcribe support for FreePBX.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

# Directory to save incoming email data
SAVE_DIR = "/tmp/received_emails"
os.makedirs(SAVE_DIR, exist_ok=True)


class EmailPayload(BaseModel):
    timestamp: str
    email: str


@router.post("/transcribe/mail")
async def receive_email(payload: EmailPayload):

    raw_email_path = f"{SAVE_DIR}/email_{payload.timestamp}.txt"
    with open(raw_email_path, "w") as f:
        f.write(payload.email)

    ###########

    msg_obj = message_from_string(payload.email)
    ep_obj = Email_Parser(msg_obj)

    ###########

    parsed_info = ep_obj.parse_email()

    msg_from = parsed_info['from']
    msg_to = parsed_info['to']
    msg_subject = parsed_info['subject']
    msg_body = parsed_info['body']
    attachment_dict = parsed_info['attachments']

    print(f"\n[{datetime.now()}] Email received and parsed:")
    print(f"→ From: {msg_from}")
    print(f"→ To: {msg_to}")
    print(f"→ Subject: {msg_subject}")

    ###########

    if "{TRANSCRIPTION}" in msg_body:
        txt = transcribe_audio(attachment_dict)
        msg_body_new = msg_body.replace("{TRANSCRIPTION}", txt)
        ep_obj.update_email(msg_body_new)

    send_email(msg_obj, msg_from, msg_to)

    return {"status": "ok"}


app.include_router(router, prefix="/api/voicemail")


if __name__ == "__main__":

    print("Starting Transcribe-Voicemail on http://localhost:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000)
