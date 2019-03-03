from email.parser import HeaderParser
import imaplib

class Mail:
    def __init__(self, conf):
        print(conf)
        self.imap = imaplib.IMAP4_SSL(conf['imap_server'], 993)
        self.imap.login(conf['user'], conf['password'])

    def get_unread_messages(self):
        msgs = []
        self.imap.select('INBOX')
        status, response = self.imap.search(None, '(UNSEEN)')
        for m in response[0].split():
            parser = HeaderParser()
            data = self.imap.fetch(m, '(RFC822)')[1][0][1]
            msg = parser.parsestr(data)
            msgs.append(msg)
        return msgs
    
