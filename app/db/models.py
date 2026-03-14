from sqlalchemy import Column, Integer, String, Float, Boolean
from .database import Base

class CallRecord(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)

    mc_number = Column(String, nullable=False)
    carrier_name = Column(String, nullable=True)
    carrier_eligible = Column(Boolean, nullable=True)

    load_id = Column(String, nullable=True)
    origin = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    pickup_datetime = Column(String, nullable=True)
    delivery_datetime = Column(String, nullable=True)
    equipment_type = Column(String, nullable=True)

    loadboard_rate = Column(Float, nullable=True)
    counteroffer = Column(Float, nullable=True)
    final_rate = Column(Float, nullable=False)

    notes = Column(String, nullable=True)
    weight = Column(Float, nullable=True)
    commodity_type = Column(String, nullable=True)
    num_of_pieces = Column(Integer, nullable=True)
    miles = Column(Float, nullable=True)
    dimensions = Column(String, nullable=True)

    negotiation_rounds = Column(Integer, nullable=False)
    outcome = Column(String, nullable=False)
    sentiment = Column(String, nullable=False)