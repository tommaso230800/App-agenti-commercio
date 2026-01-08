"""email_sender.py

Invio email con allegato (PDF) via SMTP.

Configurazione via variabili d'ambiente / Streamlit Secrets:
- SMTP_HOST (es. smtp.gmail.com)
- SMTP_PORT (465 per SSL, 587 per STARTTLS)
- SMTP_USER
- SMTP_PASS
Opzionali:
- SMTP_FROM (default: SMTP_USER)
- SMTP_SSL ("1" per SSL, default: 1 se porta 465)
- SMTP_TLS ("1" per STARTTLS, default: 1 se porta 587)
"""

from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() not in ("0", "false", "no", "off")


def send_email_with_attachment(
    *,
    to_email: str,
    subject: str,
    body: str,
    attachment_bytes: bytes,
    attachment_filename: str,
    mime_type: str = "application/pdf",
    cc: str | None = None,
    bcc: str | None = None,
) -> None:
    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "587").strip() or "587")
    user = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASS", "")
    from_addr = (os.getenv("SMTP_FROM", "").strip() or user).strip()

    if not host or not user or not password or not from_addr:
        raise RuntimeError("SMTP non configurato: imposta SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASS")

    to_email = (to_email or "").strip()
    if not to_email:
        raise RuntimeError("Destinatario email mancante")

    use_ssl = _env_bool("SMTP_SSL", default=(port == 465))
    use_tls = _env_bool("SMTP_TLS", default=(port == 587))

    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_email
    if cc:
        msg["Cc"] = cc
    msg["Subject"] = subject or "Conferma Ordine"
    msg.set_content(body or "Buongiorno,\n\nin allegato la conferma d'ordine.\n\nCordiali saluti")

    maintype, subtype = (mime_type.split("/", 1) + ["octet-stream"])[:2]
    msg.add_attachment(
        attachment_bytes,
        maintype=maintype,
        subtype=subtype,
        filename=attachment_filename or "ordine.pdf",
    )

    recipients = [to_email]
    if cc:
        recipients += [x.strip() for x in cc.split(",") if x.strip()]
    if bcc:
        recipients += [x.strip() for x in bcc.split(",") if x.strip()]

    context = ssl.create_default_context()

    if use_ssl:
        with smtplib.SMTP_SSL(host, port, context=context, timeout=25) as server:
            server.login(user, password)
            server.send_message(msg, from_addr=from_addr, to_addrs=recipients)
    else:
        with smtplib.SMTP(host, port, timeout=25) as server:
            server.ehlo()
            if use_tls:
                server.starttls(context=context)
                server.ehlo()
            server.login(user, password)
            server.send_message(msg, from_addr=from_addr, to_addrs=recipients)
