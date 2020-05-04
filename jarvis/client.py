from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
import argparse

from models import Contact

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', '-d', help="Path for jarvs.db file", default="/data/jarvis/jarvis.db")
    args = parser.parse_args()
    engine = create_engine('sqlite:///{}'.format(args.database))
    session = scoped_session(sessionmaker(bind=engine))

    contacts = session.query(Contact).all()
    print(contacts)

main()
