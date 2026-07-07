import imaplib
import email
from email.header import decode_header
import datetime

def check_pec_mail():
    username = "vasile.bratu@timpec.it*vasile.bratu"
    password = "Ari2Nicu!?"
    imap_server = "imap.pectim.it"
    
    print("Connecting to TIM PEC IMAP server...")
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
        
        # Look at the last 20 emails
        last_ids = mail_ids[-20:]
        print("\nLast 20 emails:")
        for mail_id in reversed(last_ids):
            res, msg = mail.fetch(mail_id, "(RFC822)")
            if res != "OK":
                continue
            for response in msg:
                if isinstance(response, tuple):
                    msg_obj = email.message_from_bytes(response[1])
                    subject, encoding = decode_header(msg_obj["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")
                    from_sender, encoding = decode_header(msg_obj["From"])[0]
                    if isinstance(from_sender, bytes):
                        from_sender = from_sender.decode(encoding or "utf-8")
                    date = msg_obj["Date"]
                    print(f"ID: {mail_id.decode()}, From: {from_sender}, Subject: {subject}, Date: {date}")
                    
                    if any(x in from_sender.lower() or x in subject.lower() for x in ["viktorija", "viktoria"]):
                        print("=== FOUND MATCH ===")
                        body = ""
                        if msg_obj.is_multipart():
                            for part in msg_obj.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                try:
                                    part_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    if content_type == "text/plain" and "attachment" not in content_disposition:
                                        body += part_body
                                except:
                                    pass
                        else:
                            try:
                                body = msg_obj.get_payload(decode=True).decode('utf-8', errors='ignore')
                            except:
                                pass
                        print("Body:", body[:1500])
                        print("===================")
                        
        mail.close()
        mail.logout()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_pec_mail()
