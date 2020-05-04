import logging
import imaplib
import email

logger = logging.getLogger(__name__)

class Mail:
    def __init__(self, conf):
        self.conf = conf

    def login(self):
        logger.debug("Logging into IMAP server...")
        self.imap = imaplib.IMAP4_SSL(self.conf['imap_server'], 993)
        self.imap.login(self.conf['user'], self.conf['password'])
        try:
            self.imap.select('INBOX')
        except Exception as e:
            logger.exception("Exception getting inbox: {}".format(e))
            self.imap.logout()
            self.login()

    def get_unread_messages(self):
        logger.debug("Retrieving unread email messages...")
        self.login()
        msgs = []

        status, response = self.imap.search(None, '(UNSEEN)')
        for m in response[0].split():
            try:
                data = self.imap.fetch(m.decode(), '(RFC822)')[1][0][1]
                msg = email.message_from_bytes(data)
                msgs.append(msg)
            except Exception as e:
                logger.exception("Exception parsing message: {}".format(e))
                raise
                continue
        self.imap.logout()
        return msgs
    
