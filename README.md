# Inbound Carrier Sales

Proof of concept for automating inbound carrier load sales using HappyRobot + FastAPI.

## Features
- Carrier verification
- Load search
- Offer evaluation
- Ready to connect to HappyRobot

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload