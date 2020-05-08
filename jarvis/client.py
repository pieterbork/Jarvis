from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
import argparse

from .models import User, Contact

def get_db_session(db="/data/jarvis/jarvis.db"):
    engine = create_engine('sqlite:///{}'.format(db))
    session = scoped_session(sessionmaker(bind=engine))
    return session

    contacts = session.query(Contact).all()
    print(contacts)

def startswith(word):
    session = get_db_session()
    user = session.query(User).filter(User.name.startswith(word)).first()
    return user

