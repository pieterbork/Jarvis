import time
import json
import logging
import requests

from . import *
from .base_module import BaseModule

logger = logging.getLogger(__name__)


class CommandModule(BaseModule):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    def get_get_response(self, contact, parts):
        resp = None
        parts_len = len(parts)
        if parts_len > 1:
            if parts[1] == 'pug':
                pug = json.loads(requests.get(PUGME_URL).text)
                resp = pug["pug"]
            elif parts[1] == 'cat':
                cat = json.loads(requests.get(CAT_URL).text)
                resp = cat["file"]
            elif parts[1] == 'joke':
                joke = json.loads(requests.get(JOKE_URL, headers={'Accept': 'application/json'}).text)
                resp = joke['joke']
        return resp

    def get_set_response(self, contact, parts):
        resp = None
        if parts_len > 2 and parts[1] == 'alias':
            alias = parts[2].title()
            self.set_alias(contact.user, alias)
            resp = 'Your alias has been updated to {}.'.format(alias)
        return resp

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
            if parts[0] == 'set':
                resp = self.get_set_response(contact, parts)
            elif parts[0] == 'get':
                resp = self.get_get_response(contact, parts)
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

    def get_introduction_response(self, contact, msg):
        resp = None
        parts = msg.split()
        for prefix in INTRODUCTIONS:
            if msg.startswith(prefix):
                parts = [part for part in msg.split(prefix) if part]
                break

        name = parts[0].strip()
        for char in '., ':
            name = name.replace(char, '')
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
            resp = "It's nice to meet you, {}".format(name.title())
            self.set_last(contact, 'hi')

        return resp

    def get_statement_response(self, contact, body):
        resp = None

        return "Thats, like, your opinion man."

    def get_question_response(self, contact, body):
        resp = None

        return "I'm not sure...That's a great question."

    def get_vulgar_response(self, contact, body):
        resp = None

        return "Chill out."

    def get_message_response(self, contact, body):
        resp = None
        
        if any(body.startswith(prefix) for prefix in COMMANDS):
            resp = self.get_command_response(contact, body)
        elif any(body.startswith(prefix) for prefix in GREETINGS):
            resp = self.get_greeting_response(contact, body)
        elif any(body.startswith(prefix) for prefix in INTRODUCTIONS) or contact.last == 'name':
            resp = self.get_introduction_response(contact, body)
        elif any(body.startswith(prefix) for prefix in STATEMENTS):
            resp = self.get_statement_response(contact, body)
        elif any(body.startswith(prefix) for prefix in QUESTIONS):
            resp = self.get_question_response(contact, body)
        elif any(body.startswith(prefix) for prefix in VULGARITIES):
            resp = self.get_vulgar_response(contact, body)

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
            logger.info('Checking messages.')
            messages = self.phone.get_unread_messages()
            if messages:
                self.handle_messages(messages)
            time.sleep(2)
        self.Session.remove()

    def stop(self):
        logger.info('CommandModule received stop request')
        self.process = False

