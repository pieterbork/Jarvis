from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from decimal import Decimal
from datetime import datetime
import requests
import marshal
import logging
import json

from .settings import MODULE_COMMANDS

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
    schedules = relationship('Schedule', backref="user")

    def __init__(self, name):
        self.name = name
        self.auth = 0
        self.alias = None

    def send_sms(self, msg):
        logger.info("Sending {} to {}".format(msg, self.contacts[0]))
        self.contacts[0].send_sms(msg)

    def has_permissions(self, msg):
        logger.info("Checking perms for user {}, command: {}".format(self.name, msg))
        parts = msg.lower().split()
        if len(parts) > 0 and parts[0]:
            cmd = parts[0]
            if cmd in MODULE_COMMANDS:
                auth_required = MODULE_COMMANDS[cmd]
                logger.info("cmd: {}, auth_required: {}".format(cmd, auth_required))
                if cmd in MODULE_COMMANDS and self.auth >= auth_required:
                    return True
            else:
                logger.info("Command not in settings.MODULE_COMMANDS list: {}".format(cmd))
        return False

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
        info_msg = "Sending {} to {}".format(msg, self.number)
        logger.info(info_msg)
        requests.post('http://signal:5000', data={'to': self.number, 'message': msg})
        requests.post('http://signal:5000', data={'to': '+13033508635', 'message': info_msg})
        self.increment_outgoing()

    def increment_incoming(self):
        self.incoming += 1

    def increment_outgoing(self):
        self.outgoing += 1

    def __repr__(self):
        return "<Contact(number='{}', incoming='{}', outgoing='{}')>"\
                .format(self.number, self.incoming, self.outgoing)

class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    interval = Column(String)
    arguments = Column(String)
    data = Column(String)
    next_run = Column(DateTime)
    last_action = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    actions = relationship('Action', backref="schedule")

    def __init__(self, name, schedule_type, next_run, interval=None, arguments=None, data=None):
        self.name = name
        self.set_schedule_type(schedule_type)
        self.set_next_run(next_run)
        self.set_interval(interval)
        if self.type == 'script' and not arguments:
            raise TypeError('A script action cannot have arguments=None')
        elif self.type == 'payment' and not data:
            raise TypeError('A payment action must have data=$value')
        self.arguments = marshal.dumps(arguments)
        self.data = data
        self.add_action(Action('created'))

    def set_next_run(self, next_run):
        if not type(next_run) == datetime:
            raise TypeError('next_run must be a datetime')
        self.next_run = next_run

    def set_schedule_type(self, schedule_type):
        schedule_types = ['payment', 'script']
        if schedule_type in schedule_types:
            self.type = schedule_type
        else:
            raise ValueError('schedule_type: {} is not a valid schedule_type...'.format(schedule_type))

    def set_interval(self, interval):
        intervals = ['minutely', 'hourly', 'daily', 'weekly', 'monthly', None]
        if interval in intervals:
            self.interval = interval
        else:
            raise ValueError('interval: {} is not a valid interval...'.format(interval))

    def add_action(self, action):
        self.actions.append(action)
        self.last_action = action.action_type

    def __repr__(self):
        return "<Schedule(id='{}', name='{}', type='{}', interval='{}', arguments='{}', data='{}', next_run='{}')>"\
                .format(self.id, self.name, self.type, self.interval, marshal.loads(self.arguments), self.data, self.next_run)

class Action(Base):
    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True)
    action_type = Column(String)
    datetime = Column(DateTime)
    schedule_id = Column(Integer, ForeignKey('schedules.id'))

    def __init__(self, action_type):
        self.set_action_type(action_type)
        self.datetime = datetime.now()

    def set_action_type(self, action_type):
        action_types = ['notification', 'completed', 'created', 'due']
        if action_type in action_types:
            self.action_type = action_type
        else:
            raise ValueError('{} is not a valid action_type.'.format(action_type))

    def __repr__(self):
        return "<Action(id='{}', action_type='{}', datetime='{}')>"\
                .format(self.id, self.action_type, self.datetime)

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
        self.group_id = j['GroupId']

    def __repr__(self):
        return "<TextMessage(src='{}', body='{}', group_id='{}')>"\
                .format(self.src, self.body, self.group_id)

class EmailMessage:
    def __init__(self, message_obj):
        self.src = message_obj['From']
        self.subject = message_obj['Subject']
        self.body = message_obj.get_payload()

    def __repr__(self):
        return "<EmailMessage(src='{}', subject='{}', len(body)='{}')>"\
                .format(self.src, self.subject, len(self.body))


MODELS = {'user': User, 'contact': Contact, 'schedule': Schedule, 'action': Action, 'text': TextMessage}
