from threading import Thread
import datetime
import logging
import time

from . import User, Contact, Payment
from .base_module import BaseModule

logger = logging.getLogger(__name__)

class PaymentMessage:
    def __init__(self, name, amount, platform):
        self.name = name
        self.amount = amount
        self.platform = platform

class PaymentTrackingModule(BaseModule):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    def parse_msgs(self, msgs):
        messages = []
        for msg in msgs:
            sub = msg['Subject'].replace('Fwd: ', '')

            if 'paid you' in sub:
                platform = "venmo"
                selector = 'paid you'
            elif 'sent you' in sub:
                platform = "zelle"
                selector = 'sent you'
            else:
                logger.info("Idk what this is: {}".format(sub))
                continue

            parts = sub.split(selector)
            name = parts[0].strip()
            amount = float(parts[1].replace('$',''))
            m = PaymentMessage(name, amount, platform)
            messages.append(m)

        return messages
    
    def check_overdue_payments(self):
        overdue_payments = self.session.query(Payment).filter(Payment.due > datetime.datetime.now()).all()
        if overdue_payments:
            logger.info("OVERDUE PAYMENTS DETECTED: ".format(len(overdue_payments)))
        for payment in overdue_payments:
            logger.info(payment)

    def run(self):
        logger.info('Starting PaymentTrackingModule')
        while True and self.process:
            msgs = self.mailbox.get_unread_messages()
            messages = self.parse_msgs(msgs)
            for m in messages:
                print(m)
            self.check_overdue_payments()
            time.sleep(5)

