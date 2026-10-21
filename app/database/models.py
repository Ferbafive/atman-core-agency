from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    email = Column(String)
    score = Column(Float)
    qualified = Column(Boolean)
    status = Column(String)

    def __repr__(self):
        return f"Lead(id={self.id}, nombre='{self.nombre}', email='{self.email}', score={self.score}, qualified={self.qualified}, status='{self.status}')"

    @classmethod
    def get_calified_leads(cls, session):
        return session.query(cls).filter(cls.qualified == True).all()
