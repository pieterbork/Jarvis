from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from queue import Queue
import datetime
import argparse
import logging
import time
import os

from .devices import Mail
from .models import *
from .modules import *

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
        self.db_path = args.database
        logger.info("Initiating db_connection with : {}".format(self.db_path))
        self.engine = create_engine('sqlite:///{}?{}'.format(self.db_path,"check_same_thread=false"))
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        self.session = self.Session()
        Base.metadata.create_all(self.engine)

    def run_modules(self):
        try:
            for module, attrs in self.modules.items():
                attrs['session'] = self.Session
                attrs['mailbox'] = self.mailbox
                attrs['message_q'] = self.message_q
                mod_func = globals()[module]
                logger.info("Launching {}".format(module))
                t = mod_func(attrs)
                t.start()
                self.threads.append(t)
            while True:
                m = self.message_q.get()
                if type(m) == TextMessage:
                    src = m.src
                    contact = self.session.query(Contact).filter(Contact.number == src).first()
                    if contact:
                        contact.increment_incoming()
                elif type(m) == EmailMessage:
                    pass

                logger.info("Distributing message to consumers: {}".format(m))
                for t in self.threads:
                    if t.sms_consumer and type(m) == TextMessage:
                        t._process_message(m)
                    elif t.email_consumer and type(m) == EmailMessage:
                        t._process_message(m)
                self.message_q.task_done()
                    #logger.debug("Heartbeat for {} was {}s ago".format(t, (datetime.datetime.now()-t.heartbeat).seconds))
                time.sleep(.5)
        except KeyboardInterrupt:
            logger.info("Ctrl+C, RIP threads.")
            self.Session.remove()
            for thread in self.threads:
                thread.stop()
            for thread in self.threads:
                thread.join()
        except Exception as e:
            logger.exception("Core Exception: {}".format(e))
            self.Session.remove()
            for thread in self.threads:
                thread.stop()
            for thread in self.threads:
                thread.join()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', help="Path for jarvis.cfg file.", default="/data/jarvis/jarvis.cfg")
    parser.add_argument('--database', '-d', help="Path for jarvs.db file", default="/data/jarvis/jarvis.db")
    args = parser.parse_args()

    j = Jarvis(args)
    j.run_modules()

if __name__ == "__main__":
    main()
