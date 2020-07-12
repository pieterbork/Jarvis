import datetime
import requests
import logging
import base64
import time
import json
import re

from .. import utils
from . import *
from .base_module import BaseModule

class CommandModule(BaseModule):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.sms_consumer = True

    def get_cat(self):
        r = requests.get(CAT_URL)
        cat = json.loads(r.text)
        resp = cat["file"]
        return resp

    def get_pug(self):
        r = requests.get(PUGME_URL)
        pug = json.loads(r.text)
        resp = pug["pug"]
        return resp

    def get_dad_joke(self):
        try:
            r = requests.get(JOKE_URL, headers={'Accept': 'application/json'})
            joke = json.loads(r.text)
            resp = joke['joke']
        except Exception as e:
            self.logger.exception("Error parsing joke {}".format(joke))
            resp = 'Sorry, there was an error getting your joke...'
        return resp

    def get_get_response(self, contact, parts):
        resp = None
        parts_len = len(parts)
        if parts_len > 1:
            if parts[1] == 'pug':
                resp = self.get_pug()
            elif parts[1] == 'cat':
                resp = self.get_cat()
            elif parts[1] == 'joke':
                resp = self.get_dad_joke()
        return resp

    def get_set_response(self, contact, parts):
        resp = None
        parts_len = len(parts)
        if parts_len > 2 and parts[1] == 'alias':
            alias = parts[2].title()
            self.set_alias(contact.user, alias)
            resp = 'Your alias has been updated to {}.'.format(alias)
        elif parts_len > 2 and parts[1] == 'user':
            for idx, part in enumerate(parts):
                name = None
                number = None
                if re.match(PHONE_REGEX, part):
                    name = ' '.join(parts[2:idx]).title()
                    number = part.replace('-','')
            if not name or not number:
                self.logger.info("Could not parse name and number from {}".format(parts))
                contact.send_sms("There was an error parsing that data.")
            else:
                self.logger.info("Parsed name as {} and number as {}".format(name, number))
                c = self.session.query(Contact).filter(Contact.number == number).first()
                u = self.session.query(User).filter(User.name == name).first()
                if not u:
                    u = User(name)
                if not c:
                    c = Contact(number)
                u.contacts.append(c)
                self.session.add(u)
                self.session.commit()
                contact.send_sms("Creating user: {} with contact: {}".format(u, c))
        return resp

    def get_delete_response(self, contact, parts):
        self.logger.info("get_delete_resp: {}".format(parts))
        resp = None
        parts_len = len(parts)
        if parts_len > 2:
            for name, model in MODELS.items():
                self.logger.info("{} == {} ?".format(name, parts[1]))
                if name == parts[1]:
                    try:
                        model_id = int(parts[2])
                        self.logger.info("id: {}".format(model_id))
                        obj = self.session.query(model).get(model_id)
                        self.session.delete(obj)
                        self.session.commit()
                        resp = "Deleted {} {}".format(name, user_id)
                    except Exception as e:
                        resp = "Error deleting {}: {}".format(name, e)
        return resp

    def get_list_response(self, contact, parts):
        resp = None
        parts_len = len(parts)
        objects = []
        if parts_len >= 2:
            for name,model in MODELS.items():
                if parts[1] == "{}s".format(name):
                    objects = self.session.query(model).all()
        resp = str(objects)
        return resp
    
    def get_run_response(self, contact, parts):
        resp = None
        if parts[0] == 'run':
            self.logger.info("run...")
            if len(parts) > 1 and parts[1] == 'script':
                self.logger.info("run script...")
                if len(parts) > 2:
                    for KEY,VALS in SCRIPTS.items():
                        self.logger.info("{}:{}".format(KEY, VALS))
                        if parts[2] == KEY or parts[2] in VALS['aliases']:
                            script = KEY
                            args = VALS['args']
                            resp = utils.run_script(script, args)
        return resp

    def get_command_response(self, contact, msg):
        resp = None
        if not contact.user:
            resp = "You can't issue commands until I know your name - try starting a conversation with 'Hi' next time."
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
            elif parts[0] == 'list':
                resp = self.get_list_response(contact, parts)
            elif parts[0] == 'delete':
                resp = self.get_delete_response(contact, parts)
            elif parts[0] == 'whoami':
                resp = str(contact.user)
            elif parts[0] == 'run':
                resp = self.get_run_response(contact, parts)
            else:
                self.logger.error("Unsupported command: {}".format(msg))
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
                resp = "I don't think so, {}.".format(contact.user.name)
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

        #modules
        #return '\xf0\x9f\x8d\x86'
        
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

    def process_message(self, contact, m):
        body = m.body
        self.logger.info("Command is {}".format(body))
        
        try:
            resp = self.get_message_response(contact, body.lower())
        except Exception as e:
            self.logger.exception("Exception in CommandModule... {}".format(e))
            resp = "There was an exception processing your command, sorry bb."
        if resp:
            contact.send_sms(resp)
        else:
            self.logger.info("Couldn't figure out a response...")


