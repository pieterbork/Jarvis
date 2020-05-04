from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from decimal import Decimal
import requests
import logging
import json

Base = declarative_base()

logger = logging.getLogger(__name__)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    #0 is basic, 1 is trusted, 2 is admin
    alias = Column(String)
    auth = Column(Integer)
    contacts = relationship('Contact', backref="user")
    payments = relationship('Payment', backref="user")

    def __init__(self, name):
        self.name = name
        self.auth = 0
        self.alias = None

    def send_sms(self, msg):
        logger.info("Sending {} to {}".format(msg, self.contacts[0]))
        self.contacts[0].send_sms(msg)

    def set_trusted(self):
        self.auth = 1

    def set_admin(self):
        self.auth = 2

    def __repr__(self):
        return "<User(id='{}', name='{}', alias='{}', auth='{}')>"\
                .format(self.id, self.name, self.alias, self.auth)

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    number = Column(String)
    last = Column(String)
    incoming = Column(Integer)
    outgoing = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, number):
        self.number = number
        self.incoming = 1
        self.outgoing = 0

    def send_sms(self, msg):
        requests.post('http://signal:5000', data={'to': self.number, 'message': msg})
        self.increment_outgoing()

    def increment_incoming(self):
        self.incoming += 1

    def increment_outgoing(self):
        self.outgoing += 1

    def __repr__(self):
        return "<Contact(number='{}', incoming='{}', outgoing='{}')>"\
                .format(self.number, self.incoming, self.outgoing)


class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    amount = Column(String)
    due = Column(Integer)
    #0 is unpaid, 1 is paid
    status = Column(String)
    next_due = Column(DateTime)
    notifications = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, amount, due, next_due=None):
        self.amount = str(amount)
        self.status = 0
        self.notifications = 0
        self.due = due
        self.next_due = next_due

    def complete(self):
        self.status = 1

    def __repr__(self):
        return "<Payment(id='{}', amount='{}', status='{}', due='{}', next_due='{}', notifications='{}')>"\
                .format(self.id, self.amount, self.status, self.due, self.next_due, self.notifications)

class TextMessage:
    def __init__(self, message_str):
        j = json.loads(message_str)
        self.src = j['To']
        self.body = j['Body']

    def __repr__(self):
        return "<TextMessage(src='{}', body='{}')>"\
                .format(self.src, self.body)

class EmailMessage:
    def __init__(self, message_obj):
        self.src = message_obj['From']
        self.subject = message_obj['Subject']
        self.body = message_obj.get_payload()

    def __repr__(self):
        return "<EmailMessage(src='{}', subject='{}', len(body)='{}')>"\
                .format(self.src, self.subject, len(self.body))


