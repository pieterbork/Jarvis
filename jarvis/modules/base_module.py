from threading import Thread
import datetime
import logging
import time

from ..settings import *
from . import User, Contact

class BaseModule(Thread):
    def __init__(self, conf):
        Thread.__init__(self)
        logging.basicConfig(format=conf['logging']['format'], level=conf['logging']['level'])
        self.logger = logging.getLogger('jarvis')
        self.schedule = conf['schedule']
        self.Session = conf['session']
        self.mailbox = conf['mailbox']
        self.schedule = conf['schedule']
        self.heartbeat = datetime.datetime.now()
        self.message_consumer = False
        self.sms_consumer = False
        self.email_consumer = False
        self.process = True
        self.session = self.Session()

    def create_user(self, name, contact):
        if not contact.user:
            user = User(name=name)
            user.contacts.append(contact)
            self.session.add(user)
            self.session.commit()
            if user.id == 1:
                user.set_admin()
            self.logger.info("Created user: {}".format(user))
        else:
            self.logger.info("User already exists...")

    def create_contact(self, number):
        contact = Contact(number=number)
        self.session.add(contact)
        self.session.commit()

    def set_last(self, contact, last):
        contact.last = last
        self.session.commit()

    def set_alias(self, user, alias):
        user.alias = alias
        self.session.commit()

    def _process_message(self, contact, msg):
        try:
            self.process_message(contact, msg)
        except Exception as e:
            self.logger.exception(e)

    def process_message(self, contact, msg):
        #How this module handles messages
        #Overwrite me!
        pass

    def run_scheduled_tasks(self):
        #Tasks to run every self.schedule seconds
        #Overwrite me!
        pass

    def run_loop_tasks(self):
        #Tasks to run every second
        #Overwrite me!
        pass

    def run(self):
        while True and self.process:
            now = datetime.datetime.now()
            self.run_loop_tasks()
            if now.second == 0 and now.minute % int(self.schedule) == 0:
                self.logger.debug("{}: running scheduled tasks".format(self.__class__.__name__))
                self.run_scheduled_tasks()
            time.sleep(1)

    def stop(self):
        self.logger.info('{}: received stop request'.format(self.__class__.__name__))
        self.process = False
