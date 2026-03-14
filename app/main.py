from fastapi import FastAPI
from pydantic import BaseModel, Field
import json
from pathlib import Path
from app.db.database import engine, SessionLocal
from app.db.models import Base, CallRecord
from sqlalchemy import func

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Inbound Carrier Sales API")

class CarrierRequest(BaseModel):
    mc_number: str = Field(example="123456")

class LoadSearchRequest(BaseModel):
    origin: str = Field(example="Chicago, IL")
    destination: str = Field(example="Atlanta, GA")
    equipment_type: str = Field(example="Dry Van")

class OfferRequest(BaseModel):
    load_id: str = Field(example="LD-001")
    loadboard_rate: float = Field(example=2200)
    counteroffer: float = Field(example=2300)
    round: int = Field(example=1)

class FinalizeCallRequest(BaseModel):
    mc_number: str = Field(example="123456")
    carrier_name: str | None = Field(default=None, example="Demo Carrier LLC")
    carrier_eligible: bool | None = Field(default=None, example=True)

    load_id: str | None = Field(default=None, example="LD-001")
    origin: str | None = Field(default=None, example="Chicago, IL")
    destination: str | None = Field(default=None, example="Atlanta, GA")
    equipment_type: str | None = Field(default=None, example="Dry Van")

    loadboard_rate: float | None = Field(default=None, example=2200)
    counteroffer: float | None = Field(default=None, example=2300)
    final_rate: float = Field(example=2250)

    negotiation_rounds: int = Field(example=2)
    outcome: str = Field(example="booked")
    sentiment: str = Field(example="positive")


def load_data():
    data_path = Path(__file__).parent / "data" / "loads.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/")
def root():
    return {"message": "Inbound Carrier Sales API is running"}

# ----- verify carrier eligibility -------
@app.post("/verify-carrier")
def verify_carrier(request: CarrierRequest):
    if request.mc_number == "123456":
        return {
            "eligible": True,
            "carrier_name": "Demo Carrier LLC",
            "status": "active",
            "reason": "Carrier verified"
        }
    elif request.mc_number =="999999":
        return {
            "eligible": False,
            "carrier_name": "Blocked Carrier Inc",
            "status": "inactive",
            "reason": "Carrier is not eligible to haul"
        }
    else:
        return {
            "eligible": False,
            "carrier_name": None,
            "status": "unknown",
            "reason": "Carrier not found; requires manual review"
        }

# ----- search loads in loads.json -------
@app.post("/search-loads")
def search_loads(request: LoadSearchRequest):
    loads = load_data()

    matches = [
        load for load in loads
        if load["origin"].lower() == request.origin.lower()
        and load["destination"].lower() == request.destination.lower()
        and load["equipment_type"].lower() == request.equipment_type.lower()
    ]
    return {"matches": matches[:3]}

# ----- negotiation logic for offer evaluation -------
@app.post("/evaluate-offer")
def evaluate_offer(request: OfferRequest):
    ask = request.loadboard_rate
    rounds_remaining = max(0, 3-request.round)

    if request.counteroffer <= ask:
        return {
            "decision": "accept",
            "counter_rate": request.counteroffer,
            "rounds_remaining": rounds_remaining,
        }
    if request.counteroffer <= ask * 1.05:
        midpoint = round((ask + request.counteroffer) / 2, 2)
        return {
            "decision": "counter",
            "counter_rate": midpoint,
            "message": f"I can do {midpoint} for this load.",
            "rounds_remaining": rounds_remaining
        }

    return {
        "decision": "reject",
        "counter_rate": None,
        "message": "That rate is too high for this load.",
        "rounds_remaining": rounds_remaining
    }

# ---- save final call result ------
@app.post("/finalize-call")
def finalize_call(request: FinalizeCallRequest):
    db = SessionLocal()
    try:
        call = CallRecord(
            mc_number=request.mc_number,
            carrier_name=request.carrier_name,
            carrier_eligible=request.carrier_eligible,
            load_id=request.load_id,
            origin=request.origin,
            destination=request.destination,
            equipment_type=request.equipment_type,
            loadboard_rate=request.loadboard_rate,
            counteroffer=request.counteroffer,
            final_rate=request.final_rate,
            negotiation_rounds=request.negotiation_rounds,
            outcome=request.outcome,
            sentiment=request.sentiment
        )

        db.add(call)
        db.commit()
        db.refresh(call)

        return {
            "message": "Call saved successfully",
            "call_id": call.id
        }
    finally:
        db.close()

@app.get("/metrics")
def get_metrics():
    db = SessionLocal()
    try:
        total_calls = db.query(CallRecord).count()

        booked_calls = db.query(CallRecord).filter(
            CallRecord.outcome == "booked"
        ).count()

        failed_negotiations = db.query(CallRecord).filter(
            CallRecord.outcome == "negotiation_failed"
        ).count()

        ineligible_carriers = db.query(CallRecord).filter(
            CallRecord.outcome == "ineligible_carrier"
        ).count()

        avg_final_rate = db.query(func.avg(CallRecord.final_rate)).filter(
            CallRecord.final_rate > 0
        ).scalar()

        sentiment_rows = db.query(
            CallRecord.sentiment,
            func.count(CallRecord.id)
        ).group_by(CallRecord.sentiment).all()

        sentiment_breakdown = {
            sentiment: count for sentiment, count in sentiment_rows
        }

        return {
            "total_calls": total_calls,
            "booked_calls": booked_calls,
            "failed_negotiations": failed_negotiations,
            "ineligible_carriers": ineligible_carriers,
            "avg_final_rate": round(avg_final_rate, 2) if avg_final_rate else 0,
            "sentiment_breakdown": sentiment_breakdown
        }
    finally:
        db.close()