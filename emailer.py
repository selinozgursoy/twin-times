import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from email.utils import parseaddr
from .db import list_bookmarks_today

def _plain_digest(rows):
    date = datetime.now().strftime('%A, %B %-d')
    lines = [f'TwinTimes Newsmarks — {date}', '', f'{len(rows)} saved stor{"y" if len(rows)==1 else "ies"}', '']
    for index, row in enumerate(rows, 1):
        lines.extend([f'{index}. {row["title"]}', f'   {row["source"]}', f'   {row["url"]}', ''])
    lines.append('Curated locally by TwinTimes.')
    return '\n'.join(lines)

def email_newsmarks(recipient, preview=False):
    if recipient and '@' not in parseaddr(recipient)[1]:
        raise ValueError('Enter a valid email address.')
    rows = list_bookmarks_today()
    if not rows:
        raise ValueError('There are no Newsmarks saved today yet.')
    body = _plain_digest(rows)
    if preview:
        return {'preview': body, 'count': len(rows)}
    if not recipient:
        raise ValueError('Enter the email address that should receive this digest.')
    host = os.getenv('TWIN_SMTP_HOST')
    sender = os.getenv('TWIN_SMTP_FROM') or os.getenv('TWIN_SMTP_USER')
    if not host or not sender:
        raise RuntimeError('Email is ready, but SMTP is not configured. Add TWIN_SMTP_HOST and TWIN_SMTP_FROM (plus login settings if required).')
    port = int(os.getenv('TWIN_SMTP_PORT', '587'))
    user = os.getenv('TWIN_SMTP_USER', '')
    password = os.getenv('TWIN_SMTP_PASSWORD', '')
    message = EmailMessage()
    message['Subject'] = f'TwinTimes Newsmarks — {datetime.now().strftime("%b %d")}'
    message['From'] = sender; message['To'] = recipient; message.set_content(body)
    if os.getenv('TWIN_SMTP_SSL', '').lower() in {'1','true','yes'}:
        client = smtplib.SMTP_SSL(host, port, timeout=20)
    else:
        client = smtplib.SMTP(host, port, timeout=20)
        if os.getenv('TWIN_SMTP_STARTTLS', 'true').lower() in {'1','true','yes'}:
            client.starttls()
    try:
        if user: client.login(user, password)
        client.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise RuntimeError(f'Email could not be sent: {exc}') from exc
    finally:
        try: client.quit()
        except Exception: pass
    return {'message': f'Sent {len(rows)} Newsmarks to {recipient}.', 'count': len(rows)}
