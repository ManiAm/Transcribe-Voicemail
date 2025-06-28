
# Transcribe-Voicemail

This project enables automatic transcription of received voicemails. Built to integrate with [FreePBX’s](https://www.freepbx.org/) voicemail-to-email functionality, this solution enhances accessibility and convenience by converting voice messages into text before they reach the recipient.

The system works by intercepting voicemail notification emails before they are sent. It extracts the audio attachment (typically a .wav file), performs local speech-to-text transcription using [Speak-IO](https://github.com/ManiAm/Speak-IO) project, and appends the resulting transcript to the body of the email. The modified email is then forwarded to the original recipient, now containing both the original audio file and a readable transcription of its contents.

FreePBX is deployed within a virtualized environment on my home network, providing a fully self-hosted, privacy-preserving communication platform. For details on the FreePBX setup and network environment, refer to [here](https://blog.homelabtech.dev/content/Self-hosted_PBX.html).

## Getting Started

Make sure to go over all prerequisites outlined in the [Prerequisites](Prerequisites.md) document before proceeding.

Begin by connecting to your FreePBX host and install the required dependency:

    sudo apt install jq

Next, install Docker to allow container-based services to run alongside FreePBX:

    curl -fsSL https://get.docker.com | sudo bash
    sudo usermod -aG docker $USER

You must log out and back in (or restart the shell session) after adding your user to the docker group for the permissions to take effect.

Clone the project repository to your FreePBX host:

    https://github.com/ManiAm/Transcribe-Voicemail
    cd Transcribe-Voicemail

Install the email intercept bash script:

    cp mail-process.sh /usr/local/bin
    chmod +x /usr/local/bin/mail-process.sh
    chown asterisk:asterisk /usr/local/bin/mail-process.sh

Open FreePBX web interface and go to Settings -> Voicemail Admin -> Settings -> Email Config

In the Email Body field, add the `{TRANSCRIPTION}` placeholder. This will be replaced with the transcribed text.

Set the "Mail Command" value to **/usr/local/bin/mail-process.sh**

Click "Submit" and "Apply Config"

Launch the FastAPI-based REST server that handles voicemail parsing and transcription:

    python3 main.py
