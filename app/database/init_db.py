from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

def init_db():
    engine = create_engine('sqlite:///leads.db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session

if __name__ == '__main__':
    init_db()
