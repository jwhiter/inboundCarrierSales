from fastapi import FastAPI
from pydantic import BaseModel
import json
from pathlib import Path

app = FastAPI(title="Inbound Carrier Sales API")

class CarrierRequest(BaseModel):
    mc_number: str

class LoadSearchRequest(BaseModel):
    origin: str
    destination: str
    equipment_type: str

class OfferRequest(BaseModel):
    load_id: str
    loadboard_rate: float
    counteroffer: float
    round: int

def load_data():
    data_path = Path(__file__).parent / "data" / "loads.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/")
def root():
    return {"message": "Inbound Carrier Sales API is running"}

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

@app.post("/evaluate-offer")
def evaluateoffer(request: OfferRequest):
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