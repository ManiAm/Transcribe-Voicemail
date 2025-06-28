#!/bin/sh

# Read full email from stdin
email_content=$(cat)

TRANSCRIBE_URL="http://localhost:5000"

timestamp=$(date +"%Y%m%d_%H%M%S")
logfile="/tmp/curl_full_$timestamp.log"
jsonfile="/tmp/email_payload_$timestamp.json"

printf '{ "timestamp": "%s", "email": %s }\n' "$timestamp" "$(printf '%s' "$email_content" | jq -Rs .)" > "$jsonfile"

curl -s -X POST "$TRANSCRIBE_URL/api/voicemail/transcribe/mail" \
  -H "Content-Type: application/json" \
  --data @"$jsonfile" \
  -w "\nHTTP_STATUS_CODE=%{http_code}\n" \
  >> "$logfile" 2>&1

rm -f "$jsonfile"
