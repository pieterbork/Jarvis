from threading import Thread
import logging
import time

from . import User, Contact
from .base_module import BaseModule

logger = logging.getLogger(__name__)

class PaymentTrackingModule(BaseModule):
    def __init__(self, conf):
        Thread.__init__(self)
        self.schedule = conf['schedule']
        self.mailbox = conf['mailbox']
        self.phone = conf['phone']
        self.process = True

    def run(self):
        logger.info('Starting PaymentTrackingModule')
        while True and self.process:
            msgs = self.mailbox.get_unread_messages()
            for msg in msgs:
                sub = msg['Subject'].replace('Fwd: ', '')

                if 'paid you' in sub:
                    platform = "venmo"
                    selector = 'paid you'
                elif 'sent you' in sub:
                    platform = "zelle"
                    selector = 'sent you'
                else:
                    continue

                parts = sub.split(selector)
                name = parts[0].strip()
                amount = float(parts[1].replace('$',''))

                logger.info("Received {} from {}.".format(amount, name))
            time.sleep(5)
#            if name in people:
#                person = people[name]
#                for payment in person['payments']:
#                    print(payment)
#                    if payment['amount'] == amount:
#                        print("Payment of {} from {} matches expected amount.".format(amount, name))
#                        msg = generate_message(person['name'], 'thanks')
#                        send_text(person['contact'], msg)
#                        break
#                    else:
#                        print('o fukk')
    def stop(self):
        logger.info('PaymentTrackingModule received stop request')
        self.process = False
