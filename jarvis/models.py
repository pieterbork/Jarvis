from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import requests
import json

Base = declarative_base()

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

    def send_sms(self, dst, msg):
        requests.post('http://signal:5000', data={'to': dst, 'message': msg})
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
    #0 is paid, 1 is unpaid, 2 is late
    status = Column(String)
    next_due = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, amount, due, next_due):
        self.amount = amount
        self.status = 1
        self.due = due
        self.next_due = next_due

    def complete(self):
        self.status = 0

    def __repr__(self):
        return "<Payment(amount='{}', due='{}', status='{}')>"\
                .format(self.amount, self.due, self.status)


class Message:
    def __init__(self, message_str):
        j = json.loads(message_str)
        self.src = j['To']
        self.body = j['Body']

    def __repr__(self):
        return "<Message(src='{}', body='{}')>"\
                .format(self.src, self.body)

class TextMessage:
    def __init__(self, message_str):
        j = json.loads(message_str)
        self.src = j['To']
        self.body = j['Body']

    def __repr__(self):
        return "<Message(src='{}', body='{}')>"\
                .format(self.src, self.body)

class EmailMessage:
    def __init__(self, message_str):
        j = json.loads(message_str)
        self.src = j['To']
        self.body = j['Body']

    def __repr__(self):
        return "<Message(src='{}', body='{}')>"\
                .format(self.src, self.body)

#class RecurringPayment(Base):
#    __tablename__ = 'recurringpayments'
#
#    id = Column(Integer, primary_key=True)
#    title = Column(String)
#    amount = Column(Integer)
#    occur = Column(String)
#    start = Column(DateTime)
#    end = Column(DateTime)
#    user_id = Column(Integer, ForeignKey('users.id'))
#
#    def __repr__(self):
#        return "<RecurringPayment(title='{}', amount='{}', occur='{}', start='{}', end='{}', user_id='{}')>"\
#                .format(self.title, self.amount, self.occur, self.start, self.end, self.user_id)
#
#class Payment(Base):
#    __tablename__ = 'payments'
#
#    id = Column(Integer, primary_key=True)
#    title = Column(String)
#    amount = Column(Integer)
#    recurringpayment_id = Column(Integer, ForeignKey('recurringpayments.id'))
#    user_id = Column(Integer, ForeignKey('users.id'))
#    
#    def __repr__(self):
#        return "<Payment(title='{}', amount='{}', recurringpayment_id='{}', user_id='{}')>"\
#                .format(self.title, self.amount, self.recurringpayment_id, self.user_id)
#
