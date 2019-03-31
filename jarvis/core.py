from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import datetime
import argparse
import logging
import time
import yaml
import os

from .models import Base
from .devices import *
from .modules import *

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
        self.modules = self.config.modules
        self.mail = Mail(self.config.mail)
        self.phone = Phone(self.config.phone)
        self.threads = []
        self.db_path = self.config.db['path']
        if not os.path.isfile(self.db_path):
            open(self.db_path, 'w').close()
        self.engine = create_engine('sqlite:///{}'.format(self.config.db['path']))
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        logger.setLevel(self.config.logging['level'])
        Base.metadata.create_all(self.engine)

    def run_modules(self):
        try:
            for module, attrs in self.modules.items():
                attrs['mailbox'] = self.mail
                attrs['phone'] = self.phone
                attrs['shared_session'] = self.Session
                mod_func = globals()[module]
                logger.info("Launching {}".format(module))
                t = mod_func(attrs)
                t.start()
                self.threads.append(t)
            while True:
                for t in self.threads:
                    logger.debug("Heartbeat for {} was {}s ago".format(t, (datetime.datetime.now()-t.heartbeat).seconds))
                time.sleep(3)
        except KeyboardInterrupt:
            logger.exception("Ctrl+C, RIP threads.")
            for thread in self.threads:
                thread.stop()
            for thread in self.threads:
                thread.join()
        except Exception as e:
            logger.exception("Unhandled exception: {}".format(e))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', help="Path for jarvis.cfg file.", required=True)
    args = parser.parse_args()

    j = Jarvis(args)
    j.run_modules()

if __name__ == "__main__":
    main()
