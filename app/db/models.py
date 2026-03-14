from sqlalchemy import Column, Integer, String, Float
from .database import Base

class CallRecord(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    mc_number = Column(String, nullable=False)
    load_id = Column(String, nullable=False)
    final_rate = Column(String, nullable=False)
    negotiation_rounds = Column(Integer, nullable=False)
    outcome = Column(String, nullable=False)
    sentiment = Column(String, nullable=False)