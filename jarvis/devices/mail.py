from email.parser import HeaderParser
import logging
import imaplib

logger = logging.getLogger(__name__)

class Mail:
    def __init__(self, conf):
        self.imap = imaplib.IMAP4_SSL(conf['imap_server'], 993)
        self.imap.login(conf['user'], conf['password'])

    def get_unread_messages(self):
        msgs = []
        try:
            self.imap.select('INBOX')
        except Exception as e:
            logger.exception("Exception getting inbox: {}".format(e))
            return msgs

        status, response = self.imap.search(None, '(UNSEEN)')
        for m in response[0].split():
            try:
                parser = HeaderParser()
                data = self.imap.fetch(m, '(RFC822)')[1][0][1]
                msg = parser.parsestr(data)
                msgs.append(msg)
            except Exception as e:
                logger.exception("Exception parsing message: {}".format(e))
                continue

        return msgs
    
