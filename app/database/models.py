from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
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

class Business(Base):
    __tablename__ = 'businesses'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    company_name = Column(String)
    industry = Column(String)
    employees = Column(Integer)
    revenue = Column(Float)
    contact_email = Column(String)
    phone = Column(String)
    city = Column(String)
    country = Column(String)
    website = Column(String)
    scraped_at = Column(DateTime)

    def __repr__(self):
        return f"Business(id={self.id}, company_name='{self.company_name}', industry='{self.industry}')"
