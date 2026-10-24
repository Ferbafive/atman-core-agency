from sqlalchemy import Column, Integer, String, Boolean, Float
from app.database.init_db import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=True)
    url = Column(String, unique=True, index=True)
    contact_email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    score = Column(Float, default=0.0)
    is_qualified = Column(Boolean, default=False)