from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from queue import Queue
import datetime
import argparse
import logging
import time
import sys
import os

from .devices import Mail
from .models import *
from .modules import *
from . import utils

#python3 has yaml builtin?
try:
    import yaml
except:
    import pyyaml
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class config:
    def from_dict(self, di):
        for key, value in di.items():
            setattr(self, key, value)
        return self

    def from_file(self, path):
        print(path)
        if not os.path.isfile(path):
            logger.error("File not found {}".format(path))
            raise FileNotFoundError
        with open(path, 'r') as fp:
            data = yaml.load(fp)
        self.from_dict(data)
        return self

class Jarvis:
    def __init__(self, args):
        self.config = config().from_file(args.config)
        logger.setLevel(self.config.logging['level'])
        self.mailbox = Mail(self.config.mail)
        self.modules = self.config.modules
        self.message_q = Queue()
        self.threads = []
        try:
            self.db_path = self.config.db['path']
        except:
            self.db_path = args.database
        logger.info("Initiating db_connection with : {}".format(self.db_path))
        try:
            self.engine = create_engine('sqlite:///{}?{}'.format(self.db_path,"check_same_thread=false"))
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            self.session = self.Session()
            Base.metadata.create_all(self.engine)
        except Exception as e:
            logger.exception("Error initiating database: {}".format(e))
            sys.exit(1)

    def cull_threads(self):
        for thread in self.threads:
            thread.stop()
        for thread in self.threads:
            thread.join()

    def run_modules(self):
        try:
            for module, attrs in self.modules.items():
                attrs['session'] = self.Session
                attrs['mailbox'] = self.mailbox
                attrs['message_q'] = self.message_q
                mod_func = globals()[module]
                try:
                    logger.info("Launching {}".format(module))
                    t = mod_func(attrs)
                    t.start()
                    self.threads.append(t)
                except Exception as e:
                    logger.exception("Error launching module {}: {}".format(module, e))
            while True:
                m = self.message_q.get()
                if type(m) == TextMessage:
                    src = m.src
                    logger.info("Getting contact for {}".format(src))
                    contact = self.session.query(Contact).filter(Contact.number == m.src).first()
                    if not contact:
                        logger.info("No contact for {}, not sending to modules".format(m))
                        continue
                    else:
                        contact.increment_incoming()
                    user = self.session.query(User).get(contact.user_id)
                    if not user:
                        logger.info("Pass to introduction module?")
                        continue
                    if user.has_permissions(m.body):
                        logger.info("Contact {} has permissions to run {}".format(contact, m.body))
                    else:
                        logger.info("Contact {} does not have permissions to run {}".format(contact, m.body))
                        continue
                    #If this user messaged through a group, be sure to respond to the group - not individual.
                    if m.group_id:
                        contact = utils.get_or_create_contact(self.session, user, m.group_id)
                        contact.increment_incoming()
                elif type(m) == EmailMessage:
                    pass

                logger.info("Distributing message to consumers: {}".format(m))
                for t in self.threads:
                    if t.sms_consumer and type(m) == TextMessage:
                        t._process_message(contact, m)
                    elif t.email_consumer and type(m) == EmailMessage:
                        t._process_message(m)
                self.message_q.task_done()
                    #logger.debug("Heartbeat for {} was {}s ago".format(t, (datetime.datetime.now()-t.heartbeat).seconds))
                time.sleep(.5)
        except KeyboardInterrupt:
            logger.info("Ctrl+C, RIP threads.")
            self.Session.remove()
            self.cull_threads()
        except Exception as e:
            logger.exception("Core Exception: {}".format(e))
            self.Session.remove()
            self.cull_threads()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', help="Path for jarvis.cfg file.", default="/data/jarvis/jarvis.cfg")
    parser.add_argument('--database', '-d', help="Path for jarvs.db file", default="/data/jarvis/jarvis.db")
    args = parser.parse_args()

    j = Jarvis(args)
    j.run_modules()

if __name__ == "__main__":
    main()
