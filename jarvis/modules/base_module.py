from threading import Thread
import datetime
import logging
import time

from . import User, Contact

logger = logging.getLogger(__name__)

class BaseModule(Thread):
    def __init__(self, conf):
        Thread.__init__(self)
        self.schedule = conf['schedule']
        self.phone = conf['phone']
        self.mail = conf['mailbox']
        self.Session = conf['shared_session']
        self.heartbeat = datetime.datetime.now()
        self.process = True

    def create_user(self, name, contact):
        if not contact.user:
            logger.info("Creation user for {}".format(name))
            user = User(name=name)
            user.contacts.append(contact)
            self.session.add(user)
            self.session.commit()
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

    def run(self):
        #Overwrite me!
        pass

    def stop(self):
        logger.info('Module received stop request')
        self.process = False
