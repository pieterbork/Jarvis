from threading import Thread
import time

from ..models import User, Contact
from . import BaseModule

class PaymentTrackingModule(BaseModule):
    def __init__(self, conf):
        Thread.__init__(self)
        self.schedule = conf['schedule']
        self.mailbox = conf['mailbox']
        self.phone = conf['phone']
        self.process = True
        #self.run()

    def run(self):
        print('Starting PaymentTrackingModule')
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

                print("Received {} from {}.".format(amount, name))
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
        print('PaymentTrackingModule received stop request')
        self.process = False
