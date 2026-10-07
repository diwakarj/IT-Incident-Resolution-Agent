"""
IT Incident Resolution Agent — backend.

Implements the three endpoints defined in design/tool-schema.json:
  POST /check-incident   — look up a known/active incident for an issue category
  POST /create-incident   — create a ticket, then notify Slack
  POST /notify-support     — post a formatted incident summary to Slack

In-memory storage only, per CLAUDE.md ("does not need a real database").
"""

import os
from typing import Literal, Optional

import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="IT Incident Resolution Agent — Backend")

IssueCategory = Literal["vpn", "mfa", "wifi", "password", "software_install", "other"]
Severity = Literal["P1", "P2", "P3"]

# Mock "known incidents" data. The golden demo path is the VPN/MFA outage:
# both categories surface the same active incident, per the shared root cause
# described in design/knowledge-base/vpn-troubleshooting.md and mfa-issues.md.
KNOWN_INCIDENTS = {
    "vpn": {
        "incident_id": "SYS-INC-0192",
        "workaround": (
            "Close the VPN client fully, generate a fresh code manually in the "
            "authenticator app, then reopen the VPN client and enter it manually."
        ),
        "affects": "MFA push delivery for VPN login",
    },
    "mfa": {
        "incident_id": "SYS-INC-0192",
        "workaround": (
            "Close the VPN client fully, generate a fresh code manually in the "
            "authenticator app, then reopen the VPN client and enter it manually."
        ),
        "affects": "MFA push delivery for VPN login",
    },
}

# In-memory incident counter for created tickets.
_incident_counter = 4830


def _next_incident_id() -> str:
    global _incident_counter
    _incident_counter += 1
    return f"INC-{_incident_counter}"


class CheckIncidentRequest(BaseModel):
    issue_category: IssueCategory
    description: str


class CreateIncidentRequest(BaseModel):
    employee_name: str
    issue_category: IssueCategory
    description: str
    severity: Severity
    business_impact: Optional[str] = None


class NotifySupportRequest(BaseModel):
    incident_id: str
    employee_name: str
    issue_category: IssueCategory
    severity: Severity
    description: str
    business_impact: Optional[str] = None


@app.post("/check-incident")
def check_incident(req: CheckIncidentRequest):
    known = KNOWN_INCIDENTS.get(req.issue_category)
    if known:
        return {"known_issue": True, **known}
    return {"known_issue": False}


def _post_to_slack(req: NotifySupportRequest) -> bool:
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return False

    severity_emoji = {"P1": "🚨", "P2": "🚨", "P3": "⚠️"}.get(req.severity, "⚠️")
    lines = [
        f"{severity_emoji} {req.severity} IT Incident",
        f"Employee: {req.employee_name}",
        f"Issue: {req.issue_category}",
    ]
    if req.business_impact:
        lines.append(f"Impact: {req.business_impact}")
    lines.append(f"Description: {req.description}")
    lines.append(f"Ticket: {req.incident_id}")
    text = "\n".join(lines)

    try:
        resp = requests.post(webhook_url, json={"text": text}, timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False


@app.post("/notify-support")
def notify_support(req: NotifySupportRequest):
    posted = _post_to_slack(req)
    return {"posted": posted}


@app.post("/create-incident")
def create_incident(req: CreateIncidentRequest):
    incident_id = _next_incident_id()

    slack_notified = _post_to_slack(
        NotifySupportRequest(
            incident_id=incident_id,
            employee_name=req.employee_name,
            issue_category=req.issue_category,
            severity=req.severity,
            description=req.description,
            business_impact=req.business_impact,
        )
    )

    if not slack_notified:
        return {
            "success": False,
            "error": "Failed to reach ticketing system",
            "slack_notified": False,
        }

    return {"success": True, "incident_id": incident_id, "slack_notified": True}
