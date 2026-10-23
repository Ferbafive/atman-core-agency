from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

import os
from dotenv import load_dotenv

load_dotenv()

def init_db():
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session

if __name__ == '__main__':
    init_db()
