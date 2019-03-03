from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    alias = Column(String)
    contacts = relationship('Contact', backref="user")

    def __init__(self, name):
        self.name = name
        self.alias = None

    def __repr__(self):
        return "<User(name='{}', alias='{}')>"\
                .format(self.name, self.alias)

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    data = Column(String)
    last = Column(String)
    incoming = Column(Integer)
    outgoing = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, data):
        self.data = data
        self.incoming = 1
        self.outgoing = 0

    def send_sms(self, phone, dst, msg):
        phone.send_sms(dst, msg)
        self.increment_outgoing()

    def increment_incoming(self):
        self.incoming += 1

    def increment_outgoing(self):
        self.outgoing += 1

    def __repr__(self):
        return "<User(data='{}', incoming='{}', outgoing='{}')>"\
                .format(self.data, self.incoming, self.outgoing)


#class Message(Base):
#    __tablename__ = 'messages'
#
#    id = Column(Integer, primary_key=True)
#    body = Column(String)
#    direction = Column(Integer) #direction is 0 if incoming, 1 if outgoing
#    contact_id = Column(Integer, ForeignKey('contacts.id'))
#
#    def __init__(self, body, direction):
#        self.body = body
#        self.direction = direction
#
#    def __repr__(self):
#        return "<Message(body='{}', user_id='{}')>"\
#                .format(self.body, self.payment_id, self.user_id)


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
