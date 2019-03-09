from googlevoice import Voice, settings
import logging
import time
import bs4

logger = logging.getLogger(__name__)

class Phone:
    def __init__(self, conf):
        self.voice = Voice()
        self.voice.login(email=conf['user'], passwd=conf['password'])

    def send_sms(self, number, message):
        self.voice.send_sms(number, message)

    def extractsms(self):
        """
        extractsms  --  extract SMS messages from BeautifulSoup
        tree of Google Voice SMS HTML.
        Output is a list of dictionaries, one per message.
        """
        msgitems = []
        tree = bs4.BeautifulSoup(self.voice.sms.html, "html.parser")
        conversations = tree.findAll("div", attrs={"id": True}, recursive=False)
        for conversation in conversations:
            rows = conversation.findAll(attrs={"class": "gc-message-sms-row"})
            for row in rows:
                msgitem = {"id": conversation["id"]}
                spans = row.findAll("span", attrs={"class": True}, recursive=False)
                for span in spans:
                    cl = span["class"][0].replace('gc-message-sms-', '')
                    msgitem[cl] = (" ".join(span.findAll(text=True))).strip()
                msgitems.append(msgitem)
        return msgitems

    def get_sms(self):
        try:
            self.voice.sms()
        except Exception as e:
            logger.exception('Unhandled exception in get_sms')
            return None
        return self.extractsms()

    def get_unread_ids(self):
        unread_ids = []
        try:
            msgs = self.voice.sms().messagess
        except JsonError as e:
            logger.exception('Caught JsonError')
            return None
        except Exception as e:
            logger.exception('Unhandled error getting messages.')

        for msg in msgs:
            if not msg.isRead and msg.id not in unread_ids:
                unread_ids.append(msg.id)
                msg.mark()
        return unread_ids
    
    def get_unread_messages(self):
        unread_ids = self.get_unread_ids()
        unread_msgs = []
        messages = self.get_sms()
        for index, msg in enumerate(messages):
            if msg['id'] in unread_ids and messages[index+1]['id'] != msg['id']:
                unread_msgs.append(msg)
        return unread_msgs

