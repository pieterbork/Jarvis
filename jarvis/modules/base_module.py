from threading import Thread
import datetime
import logging
import time

from ..settings import *
from . import User, Contact

logger = logging.getLogger(__name__)

class BaseModule(Thread):
    def __init__(self, conf):
        Thread.__init__(self)
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
            logger.info("Created user: {}".format(user))
        else:
            logger.info("User already exists...")

    def create_contact(self, data):
        contact = Contact(data=data)
        self.session.add(contact)
        self.session.commit()

    def set_last(self, contact, last):
        contact.last = last
        self.session.commit()

    def set_alias(self, user, alias):
        user.alias = alias
        self.session.commit()

    def has_permissions(self, contact, command):
        logger.info("has_permissions, user: {}, command: {}".format(contact.user, command))
        if command in ADMIN_CMDS and contact.user.auth == 2:
            return True
        elif command not in ADMIN_CMDS:
            return True
        return False

    def _process_message(self, msg):
        try:
            self.process_message(msg)
        except Exception as e:
            logger.exception(e)

    def process_message(self, msg):
        #Overwrite me!
        pass

    def run_scheduled_tasks(self):
        #Overwrite me!
        pass

    def run(self):
        while True and self.process:
            now = datetime.datetime.now()
            if now.second == 0 and now.minute % int(self.schedule) == 0:
                logger.debug("{}: running scheduled tasks".format(self.__class__.__name__))
                self.run_scheduled_tasks()
            time.sleep(1)

    def stop(self):
        logger.info('{}: received stop request'.format(self.__class__.__name__))
        self.process = False
