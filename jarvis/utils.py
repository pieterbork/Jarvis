import logging

from .models import Contact, User
from .scripts import *

logger = logging.getLogger("utils")

def create_user(session, name, contact):
    if not contact.user:
        user = User(name=name)
        user.contacts.append(contact)
        session.add(user)
        session.commit()
        if user.id == 1:
            user.set_admin()
        logger.info("Created user: {}".format(user))
    else:
        logger.info("User already exists...")

def create_contact(session, number):
    logger.info("Creating contact for {}".format(number))
    contact = Contact(number=number)
    session.add(contact)
    session.commit()

def add_to_db(session, obj):
    session.add(obj)
    session.commit()

def get_user_from_contact(session, contact):
    user = session.query(User).filter(User.id == contact.user_id).first()
    return user

def get_user_contact(session, user_id):
    contact = session.query(Contact).filter(Contact.user_id == user_id).first()
    return contact

def get_or_create_contact(session, user, number):
    contact = session.query(Contact).filter(Contact.user_id == user.id).filter(Contact.number == number).first()
    if not contact:
        contact = Contact(number=number)
        user.contacts.append(contact)
        add_to_db(session, user)

def create_user(session, name, contact):
    if not contact.user:
        user = User(name=name)
        user.contacts.append(contact)
        session.add(user)
        session.commit()
        if user.id == 1:
            user.set_admin()
            session.add(user)
            session.commit()
        logger.info("Created user: {}".format(user))
        return user
    else:
        logger.info("User already exists...")

def create_contact(session, number):
    contact = Contact(number=number)
    session.add(contact)
    session.commit()
    return contact

def run_script(name, args={}):
    logger.info("Running script: {} with args: {}".format(name, args))
    script_function = globals()[name]
    output = script_function(**args)
    return output

def get_datetime(datestr):
    dt = None
    formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f"]

    for fmt in formats:
        try:
            dt = datetime.strptime(datestr, fmt)
            break
        except:
            pass
    if not dt:
        raise ValueError("Couldn't parse {} to a datetime".format(datestr))
    return dt

def get_user(session, name):
    user = session.query(User).filter(name == User.name).all()
    if not user:
        logger.info("Using startswith to find user...")
        user = session.query(User).filter(User.name.startswith(name)).all()
    return user

def get_user_from_name(session, name):
    user = get_user(session, name.title())
    if len(user) > 1:
        logger.info("Found more than one user for query {}: {}".format(name, user))
        for u in user:
            print(u)
    elif user:
        user = user[0]
    else:
        parts = name.split()
        first_name = parts[0]
        logger.info("Couldn't find a user with name: {}, searching for {}".format(name, first_name))
        user = get_user(session, first_name.title())
        if user:
            user = user[0]

    return user
