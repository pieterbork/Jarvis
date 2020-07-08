from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from collections import OrderedDict
from datetime import datetime,timedelta
import requests
import logging

from .models import *
from . import utils

logger = logging.getLogger("scripts")

def get_db_session(db="/etc/jarvis/jarvis.db"):
    engine = create_engine('sqlite:///{}'.format(db))
    session = scoped_session(sessionmaker(bind=engine))
    return session

def get_place_id(location=None):
    if not location:
        raise TypeError('location cannot be None')
    url = "https://api.recollect.net/api/areas/Longmont/services/602/address-suggest?q={}&locale=en-US"\
            .format('+'.join(location.split()))
    resp = requests.get(url)
    j = resp.json()
    try:
        place_id = j[0]['place_id']
    except:
        raise ValueError('Could not get place!')
    return place_id

def get_trash_schedule(location=None, days=7):
    logger.info("Running get_trash_schedule with location={} and days={}".format(location, days))
    if not location:
        raise TypeError('location cannot be none')
    place = get_place_id(location)
    output_events = OrderedDict({})
    after = datetime.now()
    before = after + timedelta(days)
    after_str = after.strftime("%Y-%m-%d")
    before_str = before.strftime("%Y-%m-%d")
    url = "https://api.recollect.net/api/places/{}/services/602/events?nomerge=1&after={}&before={}&locale=en-US"\
            .format(place, after_str, before_str)
    resp = requests.get(url)
    j = resp.json()
    for event in j['events']:
        day = event['day']
        if 'type' in event:
            if event['type'] == 'holiday':
                output_events[day] = ['holiday']
        else:
            flags = event['flags'][0]
            sub = flags['subject']
            if day in output_events:
                output_events[day].append(sub)
            else:
                output_events[day] = [sub]
    output = "Collection Schedule:"
    for key,vals in output_events.items():
        output += "\n{} - {}".format(key, '/'.join(vals))
    return output

def notify_overdue_payments():
    session = get_db_session()
    overdue_payments = session.query(Payment)\
            .filter(Payment.status == 0)\
            .filter(Payment.due < datetime.now()).all()
    for p in overdue_payments:
        days_overdue = (datetime.now() - utils.get_datetime(p.due)).days
        u = session.query(User).get(p.user_id)
        c = u.contacts[0]
        msg = "Your bill of {} is {} days overdue. Pay up or a an automatic 6% late fee will be applied.".format(p.amount, days_overdue)
        c.send_sms(msg)





