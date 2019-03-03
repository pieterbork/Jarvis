from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import modules
import time
import yaml

from models import Base
from mail import Mail
from phone import Phone

class config:
    def from_dict(self, di):
        for key, value in di.items():
            setattr(self, key, value)

    def from_file(self, path):
        with open(path) as fp:
            data = yaml.load(fp)
        self.from_dict(data)
        return self

class Jarvis:
    def __init__(self):
        self.config = config().from_file('jarvis.cfg')
        self.modules = self.config.modules
        self.mail = Mail(self.config.mail)
        self.phone = Phone(self.config.phone)
        self.threads = []
        self.engine = create_engine('sqlite:///jarvis.db')
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        Base.metadata.create_all(self.engine)

    def run_modules(self):
        try:
            for module, attrs in self.modules.items():
                attrs['mailbox'] = self.mail
                attrs['phone'] = self.phone
                attrs['shared_session'] = self.Session
                mod_func = getattr(modules, module)
                t = mod_func(attrs)
                t.start()
                self.threads.append(t)
            while True:
                time.sleep(3)
        except KeyboardInterrupt:
            print("Ctrl+C, RIP threads.")
            for thread in self.threads:
                thread.stop()
            for thread in self.threads:
                thread.join()
        except:
            print("Unhandled exception")

j = Jarvis()
j.run_modules()
