import os, smtplib, requests
from email.mime.text import MIMEText

ALERT_THRESHOLD = int(os.getenv("ALERT_THRESHOLD", 7))
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO")
SMTP_HOST = os.getenv("SMTP_HOST"); SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER"); SMTP_PASS = os.getenv("SMTP_PASS")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def _email_enabled(): return all([ALERT_EMAIL_TO, SMTP_HOST, SMTP_USER, SMTP_PASS])
def _slack_enabled(): return bool(SLACK_WEBHOOK_URL)

def _send_email(subject: str, body: str):
    if not _email_enabled(): return
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject; msg["From"] = SMTP_USER; msg["To"] = ALERT_EMAIL_TO
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls(); s.login(SMTP_USER, SMTP_PASS); s.sendmail(SMTP_USER, [ALERT_EMAIL_TO], msg.as_string())

def maybe_alert(record: dict):
    if int(record.get("risk_point", 0)) < ALERT_THRESHOLD: return
    title = record.get("title"); src = record.get("source")
    rp = record.get("risk_point"); cat = record.get("category"); tox = record.get("toxicity")
    hits = ", ".join(record.get("rule_hits", []))
    body = f"""High-risk news detected:
Title: {title}
Source: {src}
Category: {cat} | Toxicity: {tox}
Risk: {rp}
Rules: {hits}
"""
    _send_email(f"[ALERT] Risk {rp}: {title}", body)
    _send_slack(f":rotating_light: Risk {rp} | {cat} | {title}\n{src}\n{hits}")
