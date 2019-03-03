import time
import logging

from . import User, Contact
from .base_module import BaseModule

logger = logging.getLogger(__name__)

class CommandModule(BaseModule):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    def get_command_response(self, contact, msg):
        resp = None
        if not contact.user:
            resp = "You can't issue commands until you have a name."
        elif msg.startswith('help'):
            resp = "Please visit https://git.io/fhAbW for available commands."
        elif msg.startswith('ping'):
            resp = 'pong'
        else:
            parts = msg.split()
            parts_len = len(parts)
            if parts[0] == 'set':
                if parts_len > 2 and parts[1] == 'alias':
                    alias = parts[2]
                    self.set_alias(contact.user, alias)
                    resp = 'Your alias has been updated to {}.'.format(alias)
        return resp

    def get_greeting_response(self, contact, msg):
        resp = None
        if contact.user:
            if contact.user.alias:
                name = contact.user.alias
            else:
                name = contact.user.name
            resp = "Hey, {}! What can I help you with?".format(name)
        else:
            resp =  "Hey, I'm Jarvis. What's your name?"
            self.set_last(contact, 'name')
        return resp

    def get_name_response(self, contact, msg):
        resp = None
        name_prefixes = ["my name is", "im", "i'm"]
        parts = msg.split()
        for prefix in name_prefixes:
            if msg.startswith(prefix):
                parts = [part for part in msg.split(prefix) if part]
                break

        name = parts[0].strip()
        for char in '., ':
            name.replace(char, '')
        name = name.title()

        if len(name.split()) > 1:
            return resp

        if contact.user:
            if name.title() == contact.user.name:
                resp = "I already know that."
                self.set_last(contact, 'yes')
            else:
                resp = "I don't think so..."
                self.set_last(contact, 'no')
        else:
            self.create_user(name, contact)
            resp = "Hi {}".format(name.title())
            self.set_last(contact, 'hi')

        return resp

    def get_message_response(self, contact, body):
        resp = None
        greeting_prefixes = ['hello', 'hi', 'hey']
        cmd_prefixes = ['ping', 'help', 'get', 'set']
        name_prefixes = ['my name is', 'im', "i'm"]
        
        if any(body.startswith(prefix) for prefix in cmd_prefixes):
            resp = self.get_command_response(contact, body)
        elif any(body.startswith(prefix) for prefix in greeting_prefixes):
            resp = self.get_greeting_response(contact, body)
        elif any(body.startswith(prefix) for prefix in name_prefixes) or contact.last == 'name':
            resp = self.get_name_response(contact, body)

        return resp

    def handle_messages(self, messages):
        for message in messages:
            src = message['from']
            logger.info("Received {} from {}".format(message, src))
            contact = self.session.query(Contact).filter(Contact.data == src).first()
            if not contact:
                contact = Contact(src)
                self.session.add(contact)
                self.session.commit()
                
            body = message['text'].lower()
            resp = self.get_message_response(contact, body)
            if resp:
                logger.info("Sending {} to {}".format(resp, src))
                contact.send_sms(self.phone, src, resp)
    
    def run(self):
        logger.info('Starting CommandModule')
        self.session = self.Session()
        while True and self.process:
            messages = self.phone.get_unread_messages()
            if messages:
                self.handle_messages(messages)
            time.sleep(2)
        self.Session.remove()

    def stop(self):
        logger.info('CommandModule received stop request')
        self.process = False

