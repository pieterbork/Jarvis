from datetime import date,datetime,timedelta
from decimal import *
import calendar
import logging
import time

from . import User, Contact, Payment, TextMessage, EmailMessage
from .base_module import BaseModule

logger = logging.getLogger(__name__)

#PaymentMessage used in this module only
class PaymentMessage:
    def __init__(self, name, amount, platform):
        self.name = name
        self.amount = str(amount)
        self.platform = platform

    def __repr__(self):
        return "<PaymentMessage(name='{}', amount='{}', platform='{}')>"\
                .format(self.name, self.amount, self.platform)

class PaymentModule(BaseModule):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.email_consumer = True
        self.sms_consumer = True
    
    def get_overdue_unnotified_payments(self):
        overdue_payments = self.session.query(Payment).filter(Payment.due < datetime.now()).filter(Payment.notifications == 0).all()
        return overdue_payments

    def parse_payment_msg_from_email(self, msg):
        sub = msg.subject

        if 'paid you' in sub:
            platform = "venmo"
            selector = 'paid you'
        elif 'sent you' in sub:
            platform = "zelle"
            selector = 'sent you'
        else:
            logger.info("Idk what this is: {}".format(sub))
            raise Exception("parse_payment_msg_from_email, new kind of message?")
        parts = sub.split(selector)
        name = parts[0].strip()
        amount = Decimal(parts[1].replace('$',''))
        m = PaymentMessage(name, amount, platform)
        return m

    def parse_payment_msg_from_text(self, msg):
        pass

    def get_user_from_name(self, name):
        user = self.session.query(User).filter(name.title() == User.name).all()
        if len(user) > 1:
            logger.info("Found more than one user for query {}: {}".format(name, user))
        elif user:
            user = user[0]
        else:
            print("Couldn't find a user...")
        return user

    def get_contact_from_number(self, number):
        contact = self.session.query(Contact).filter(Contact.number == number).first()
        return contact

    def get_first_day_next_month(self, dt):
        start_date = dt
        if start_date.day == 1:
            start_date += timedelta(1)
        while start_date.day != 1:
            start_date += timedelta(1)
        return start_date

    def get_datetime_from_expr(self, date_expr):
        pass

    def is_due_repeating(self, expr):
        if 'every' in expr:
            return True
        return False

    def get_payment(self, amount, date_expr_parts):
        p = None
        date_expr = ' '.join(date_expr_parts)
        today = datetime.now()
        if not date_expr_parts or date_expr_parts[0] == 'now':
            p = Payment(amount=amount, due=today)
        elif date_expr_parts[0] == 'tomorrow':
            today = today.replace(hour=12, minute=0, second=0)
            tomorrow = today + timedelta(1)
            p = Payment(amount=amount, due=tomorrow)
        elif all(s in date_expr for s in ['every', 'month']):
            today = today.replace(hour=12, minute=0, second=0)
            if any(s in date_expr for s in ['begin', 'start']):
                if today.day == 1:
                    due_date = today
                else:
                    due_date = self.get_first_day_next_month(today)
                p = Payment(amount=amount, due=due_date, next_due=self.get_first_day_next_month(due_date))
            else:
                logger.info("Could not parse {}".format(date_expr))
        else:
            logger.info("Couldn't even get close to parsing {}".format(date_expr))

        print(p)
        return p

    def schedule_payment(self, user, payment):
        user.payments.append(payment)
        self.session.add(user)
        self.session.commit()
        logger.info("Scheduled payment: {} for {}".format(payment, user))

    def delete_payment(self, payment):
        self.session.delete(payment)
        self.session.commit()
        logger.info("Deleted payment: {}".format(payment))
        
    def process_message(self, msg):
        if type(msg) == TextMessage:
            resp = None
            contact = self.get_contact_from_number(msg.src)
            parts = msg.body.lower().split(' ')
            if parts[0] in ['bill', 'charge']:
                try:
                    dollar_amount = [s for s in parts if "$" in s][0]
                except Exception as e:
                    raise e
                amount = Decimal(dollar_amount.strip("$"))
                i = parts.index(dollar_amount)
                name = ' '.join(parts[1:i]).replace(' for', '')
                date_expr_parts = parts[i+1:]
                payment = self.get_payment(amount, date_expr_parts)
                user = self.get_user_from_name(name) 
                if user:
                    self.schedule_payment(user, payment)
                    resp = "Scheduled payment_id: {} for user: {}".format(payment.id, user.name)
            elif parts[0] in ['cancel', 'delete'] and parts[1] == 'payment':
                try:
                    payment_id = int(parts[2])
                except Exception as e:
                    logger.exception("Could not parse payment ID: {}".format(parts))
                    return
                p = self.session.query(Payment).get(payment_id)
                if p:
                    self.delete_payment(p)
                    resp = "Deleted payment_id: {}".format(p.id)
                else:
                    resp = "No such payment_id exists."

            if resp:
                logger.info("Sending {} to {}".format(resp, contact.number))
                contact.send_sms(resp)
                
        elif type(msg) == EmailMessage:
            if any(["venmo", "zelle"]) in msg.subject:
                pm = parse_payment_message_from_email(msg)

    def run_scheduled_tasks(self):
        payments = self.get_overdue_unnotified_payments()
        if len(payments) > 0:
            print("THESE OVERDUE AND UNNOTIFIED SON")
        for p in payments:
            user = p.user
            # needs to be enabled to send to actual contact
            #c = user.contacts[0]
            c = self.session.query(Contact).get(1)
            logger.info("Sending notification for {}".format(p))
            c.send_sms("{} owes Pieter {} - best pay up...".format(user, p.amount))
            p.notifications += 1
            self.session.add(p)
            self.session.commit()


