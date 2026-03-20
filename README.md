# Inbound Carrier Sales API

This project is a proof of concept for automating inbound carrier load sales using FastAPI. It simulates a backend system that can verify carriers, search for loads, evaluate offers, and record call outcomes.

## Features

- **Carrier Verification**: Check if a carrier is eligible to haul loads.
- **Load Search**: Find available loads based on origin, destination, and equipment type.
- **Offer Evaluation**: Programmatically evaluate and respond to carrier offers.
- **Call Tracking**: Save call details and negotiation outcomes to a database.
- **Metrics Dashboard**: Basic endpoint to view call metrics.
- **Ready to Connect**: Designed to be integrated with a voice AI system like HappyRobot.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.10+
- An active virtual environment

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd inboundCarrierSales
    ```

2.  **Create and activate a virtual environment:**

    For Windows:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```

    For macOS/Linux:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the dependencies:**
    The project uses `pyproject.toml` to manage dependencies. Install them using pip:
    ```bash
    pip install .
    ```
    This will install FastAPI, Uvicorn, SQLAlchemy, and other required packages.

    For deployment platforms that expect a `requirements.txt`, a minimal one is included.

## Usage

To run the FastAPI application, use the following command:

```bash
uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`. You can access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## Security

This API requires an API key for all endpoints.

### Local setup

Set an API key in `.env` (the app loads it automatically):

```env
API_KEY=<your-strong-key>
```

Example call:

```bash
curl -H "X-API-Key: <your-strong-key>" http://127.0.0.1:8000/metrics
```

### Carrier Verification (FMCSA)

The challenge expects carrier verification against the official FMCSA database. In this proof of concept, the `/verify-carrier` endpoint is currently **stubbed** to return deterministic demo responses while the FMCSA API key is pending. The endpoint is wired to accept the MC number and can be upgraded to a live FMCSA lookup once the key is available.

If you are reviewing the demo without the FMCSA key:
- The end-to-end workflow still runs.
- Carrier verification should be considered a mocked step.

### HTTPS

Local HTTPS (self-signed):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile .\certs\key.pem --ssl-certfile .\certs\cert.pem
```

In cloud deployments, use the provider's managed HTTPS (or Let's Encrypt) on the public endpoint.

## Deployment (example: Render)

This section shows one clear, reproducible path to deploy the API. You can follow the same steps on other providers (Railway, Fly.io, etc.).

### 1) Build/start command

Render will run your web service with this command:

```bash
pip install .
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 2) Environment variables

Set the following env vars in the Render dashboard:

```text
API_KEY=<your-strong-key>
```

### 3) Create the service (manual steps)

1. Create a new Web Service from this repository.
2. Choose Python as the runtime.
3. Set the build and start commands (above).
4. Add the `API_KEY` env var.
5. Deploy.

After deploy, your API will be accessible at your Render URL, for example:
`https://your-service.onrender.com`.

### 4) Verify deployment

```bash
curl -H "X-API-Key: <your-strong-key>" https://your-service.onrender.com/metrics
```

### 5) Reproduce the deployment

Use the same steps above in the Render dashboard, or automate it with Terraform by creating:
- A Render Web Service using this repo
- An env var `API_KEY`
- A start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Dashboard deployment (optional)

If you deploy the Streamlit dashboard, set:

```text
API_URL=https://your-service.onrender.com/metrics
API_KEY=<your-strong-key>
```

Run it with:

```bash
streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port $PORT
```

### Azure App Service (Dashboard)

If deploying the dashboard to a separate Azure App Service:

1. Create a Linux Python Web App.
2. Set Startup Command:
   ```bash
   python -m streamlit run dashboard/app.py --server.port 8000 --server.address 0.0.0.0
   ```
3. App settings:
   ```text
   API_URL=https://inboundcarriersales-wa4c-e5bkf3e9eydaarar.spaincentral-01.azurewebsites.net/metrics
   API_KEY=<your-strong-key>
   SCM_DO_BUILD_DURING_DEPLOYMENT=true
   WEBSITES_PORT=8000
   ```

## Deployed URLs

API:
`https://inboundcarriersales-wa4c-e5bkf3e9eydaarar.spaincentral-01.azurewebsites.net`

Dashboard:
`https://inboundcarriersales-wa-awdkgta3gqbjgpbr.spaincentral-01.azurewebsites.net`


## Project Structure

```
inboundCarrierSales/
�
+-- .gitignore
+-- calls.db            # SQLite database for call records
+-- pyproject.toml      # Project configuration and dependencies
+-- requirements.txt    # Minimal deps for deployment platforms
+-- README.md           # This file
�
+-- app/
�   +-- main.py         # FastAPI application logic and endpoints
�   +-- data/
�   �   +-- loads.json  # Sample load data
�   +-- db/
�       +-- database.py # Database session and engine setup
�       +-- models.py   # SQLAlchemy database models
�
+-- dashboard/
    +-- app.py          # Streamlit dashboard
```

## API Endpoints

The following are the main endpoints available in the API:

- `GET /`: Root endpoint, returns a welcome message.
- `POST /verify-carrier`: Verifies carrier eligibility based on their MC number.
- `POST /search-loads`: Searches for available loads from `data/loads.json`.
- `POST /evaluate-offer`: Evaluates a carrier's offer on a load.
- `POST /finalize-call`: Records the final details of a call negotiation into `calls.db`.
- `GET /metrics`: Provides simple analytics on call outcomes.

For detailed request and response models, please see the auto-generated documentation at `/docs`.
