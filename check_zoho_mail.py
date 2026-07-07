import imaplib
import email
from email.header import decode_header
import datetime

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def check_mail():
    username = "amendamax@vasiledev.com"
    password = "Ari2Nicu!"
    imap_server = "imap.zoho.eu"
    
    print("Connecting to Zoho IMAP server...")
    try:
        # connect to server
        mail = imaplib.IMAP4_SSL(imap_server, 993)
        # login
        mail.login(username, password)
        print("Logged in successfully!")
        
        # select inbox
        mail.select("inbox")
        
        # search for all emails
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            print("No messages found!")
            return
            
        mail_ids = messages[0].split()
        print(f"Total emails: {len(mail_ids)}")
        
        # Look at the last 15 emails
        last_ids = mail_ids[-15:]
        print("\nLast 15 emails:")
        for mail_id in reversed(last_ids):
            # fetch the email body (RFC822) for the given ID
            res, msg = mail.fetch(mail_id, "(RFC822)")
            if res != "OK":
                continue
            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg_obj = email.message_from_bytes(response[1])
                    # decode the email subject
                    subject, encoding = decode_header(msg_obj["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to string
                        subject = subject.decode(encoding or "utf-8")
                    # decode email sender
                    from_sender, encoding = decode_header(msg_obj["From"])[0]
                    if isinstance(from_sender, bytes):
                        from_sender = from_sender.decode(encoding or "utf-8")
                    date = msg_obj["Date"]
                    print(f"ID: {mail_id.decode()}, From: {from_sender}, Subject: {subject}, Date: {date}")
                    
                    # If subject or sender has viktorija, print more details
                    if "viktorija" in from_sender.lower() or "viktorija" in subject.lower() or "viktoria" in from_sender.lower() or "viktoria" in subject.lower():
                        print("=== FOUND MATCH ===")
                        body = ""
                        if msg_obj.is_multipart():
                            for part in msg_obj.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                try:
                                    # get the email body
                                    part_body = part.get_payload(decode=True).decode()
                                    if content_type == "text/plain" and "attachment" not in content_disposition:
                                        body += part_body
                                except:
                                    pass
                        else:
                            try:
                                body = msg_obj.get_payload(decode=True).decode()
                            except:
                                pass
                        print("Body:", body[:1000])
                        print("===================")
                        
        mail.close()
        mail.logout()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mail()
