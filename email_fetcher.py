import imaplib
import email
from email.header import decode_header

def fetch_latest_email(username, password, imap_server='imap.outlook.com', folder='INBOX'):
    # Connect and login
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    mail.select(folder)

    # Search unread or specific subject
    status, messages = mail.search(None, '(UNSEEN SUBJECT "Margin Report")')
    
    email_ids = messages[0].split()
    if not email_ids:
        print("No matching unread emails found.")
        return None

    # Get latest email ID
    latest_email_id = email_ids[-1]
    status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
    
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            print("Subject:", subject)

            # Extract email body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            return {
                'subject': subject,
                'body': body
            }

    return None
