from googlevoice import Voice, settings
import time
import bs4


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
        self.voice.sms()
        return self.extractsms()

    def list_folders(self):
        folder = self.voice.search('all')
        for i in folder.messages:
            print(i, i.phoneNumber, i.type)

    def get_unread_ids(self):
        unread_ids = []
        for msg in self.voice.sms().messages:
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

    def print_feeds(self):
        for feed in settings.FEEDS:
            print(feed.title())
            for msg in getattr(self.voice, feed)().messages:
                print(msg)


