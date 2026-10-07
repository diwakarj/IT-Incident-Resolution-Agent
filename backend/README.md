# Backend — IT Incident Resolution Agent

FastAPI backend implementing the three tool endpoints in `design/tool-schema.json`.

## Run it

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
uvicorn main:app --reload
```

Server runs at `http://127.0.0.1:8000`.

If `SLACK_WEBHOOK_URL` is unset or the Slack call fails, `/create-incident`
returns `success: false` (see below) instead of a silent success — this is
what lets the agent follow the failure-handling branch instead of falsely
confirming the ticket was created.

## Expose it for ElevenLabs (local dev only)

ElevenLabs' servers need to reach this API over the internet, so during
local testing expose it with ngrok:

```bash
ngrok http 8000
```

Use the resulting `https://<random>.ngrok-free.app` URL as the base URL when
configuring the custom tools in the ElevenLabs dashboard.

## Endpoints

### `POST /check-incident`

```bash
curl -X POST http://127.0.0.1:8000/check-incident \
  -H "Content-Type: application/json" \
  -d '{"issue_category": "vpn", "description": "VPN says authentication failed"}'
```

Known issue response:

```json
{
  "known_issue": true,
  "incident_id": "SYS-INC-0192",
  "workaround": "Close the VPN client fully, generate a fresh code manually in the authenticator app, then reopen the VPN client and enter it manually.",
  "affects": "MFA push delivery for VPN login"
}
```

`vpn` and `mfa` are the only categories with a mocked known incident (the
golden-path VPN/MFA outage). Any other category returns:

```json
{ "known_issue": false }
```

### `POST /create-incident`

```bash
curl -X POST http://127.0.0.1:8000/create-incident \
  -H "Content-Type: application/json" \
  -d '{
        "employee_name": "Diwakar",
        "issue_category": "vpn",
        "description": "VPN authentication failing, workaround attempted but did not resolve",
        "severity": "P2",
        "business_impact": "Blocking a customer meeting in 30 minutes"
      }'
```

Success:

```json
{ "success": true, "incident_id": "INC-4831", "slack_notified": true }
```

Failure (e.g. `SLACK_WEBHOOK_URL` missing/invalid or Slack unreachable):

```json
{ "success": false, "error": "Failed to reach ticketing system", "slack_notified": false }
```

### `POST /notify-support`

Posts a formatted message to the IT support Slack channel. Called
internally by `/create-incident`; exposed as its own endpoint for modularity
and independent testing.

```bash
curl -X POST http://127.0.0.1:8000/notify-support \
  -H "Content-Type: application/json" \
  -d '{
        "incident_id": "INC-4831",
        "employee_name": "Diwakar",
        "issue_category": "vpn",
        "severity": "P2",
        "business_impact": "Blocking a customer meeting in 30 minutes",
        "description": "VPN authentication failing, workaround attempted but did not resolve"
      }'
```

```json
{ "posted": true }
```
