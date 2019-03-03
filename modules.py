from threading import Thread
from models import User, Contact
import time

class Module(Thread):
    def __init__(self, conf):
        Thread.__init__(self)
        self.schedule = conf['schedule']
        self.phone = conf['phone']
        self.Session = conf['shared_session']
        self.process = True

    def create_user(self, name, contact):
        if not contact.user:
            print("Creation user for {}".format(name))
            user = User(name=name)
            user.contacts.append(contact)
            self.session.add(user)
            self.session.commit()
        else:
            print("User already exists...")

    def create_contact(self, data):
        contact = Contact(data=data)
        self.session.add(contact)
        self.session.commit()

    def set_last(self, contact, last):
        contact.last = last
        self.session.commit()

    def set_alias(self, user, alias):
        user.alias = alias
        self.session.commit()

    def run(self):
        #Overwrite me!
        pass

    def stop(self):
        print('Module received stop request')
        self.process = False


class CommandModule(Module):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    def get_command_response(self, contact, msg):
        resp = None
        if not contact.user:
            resp = "You can't issue commands until you have a name."
        elif msg.startswith('help'):
            resp = "Please visit https://git.io/testing for available commands."
        elif msg.startswith('ping'):
            resp = 'pong'
        else:
            parts = msg.split()
            parts_len = len(parts)
            if parts[0] == 'set':
                if parts_len > 2 and parts[1] == 'alias':
                    alias = parts[2]
                    self.set_alias(contact.user, alias)
                    resp = 'Your alias has been updated to {}.'.format(alias)
        return resp

    def get_greeting_response(self, contact, msg):
        resp = None
        if contact.user:
            if contact.user.alias:
                name = contact.user.alias
            else:
                name = contact.user.name
            resp = "Hey, {}! What can I help you with?".format(name)
        else:
            resp =  "Hey, I'm Jarvis. What's your name?"
            self.set_last(contact, 'name')
        return resp

    def get_name_response(self, contact, msg):
        resp = None
        name_prefixes = ["my name is", "im", "i'm"]
        parts = msg.split()
        for prefix in name_prefixes:
            if msg.startswith(prefix):
                parts = [part for part in msg.split(prefix) if part]
                break

        name = parts[0].strip()
        for char in '., ':
            name.replace(char, '')
        name = name.title()

        if contact.user:
            if name.title() == contact.user.name:
                resp = "Yes, yes it is."
            else:
                resp = "I don't think so..."
        else:
            self.create_user(name, contact)

        resp = "Hi {}".format(name.title())
        self.set_last(contact, 'hi')
        return resp

    def get_message_response(self, contact, body):
        resp = None
        greeting_prefixes = ['hello', 'hi', 'hey']
        cmd_prefixes = ['ping', 'help', 'get', 'set']
        name_prefixes = ['my name is', 'im', "i'm"]

        if any(body.startswith(prefix) for prefix in cmd_prefixes):
            resp = self.get_command_response(contact, body)
        elif any(body.startswith(prefix) for prefix in greeting_prefixes):
            resp = self.get_greeting_response(contact, body)
        elif any(body.startswith(prefix) for prefix in name_prefixes) or contact.last == 'name':
            resp = self.get_name_response(contact, body)

        return resp

    def handle_messages(self, messages):
        for message in messages:
            print(message)
            src = message['from']
            contact = self.session.query(Contact).filter(Contact.data == src).first()
            if not contact:
                contact = Contact(src)
                self.session.add(contact)
                self.session.commit()
                
            body = message['text'].lower()
            resp = self.get_message_response(contact, body)
            if resp:
                print("Sending {} to {}".format(resp, src))
                contact.send_sms(self.phone, src, resp)
    
    def run(self):
        print('Starting CommandModule')
        self.session = self.Session()
        while True and self.process:
            messages = self.phone.get_unread_messages()
            if messages:
                self.handle_messages(messages)
            time.sleep(2)
        self.Session.remove()

    def stop(self):
        print('CommandModule received stop request')
        self.process = False

class PaymentTrackingModule(Thread):
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


