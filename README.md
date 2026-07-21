# Task Tracker API

Minimal FastAPI REST API skeleton for the Module 1 Task Tracker learning project.

This project is intentionally small and local-first. It currently includes only:

- A FastAPI application instance
- A `/health` endpoint
- A SQLite-ready data folder for future database work

It does not include CRUD endpoints yet. It also does not include authentication, user accounts, Docker, cloud deployment, frontend files, notifications, real-time updates, or a production database setup.

## Project structure

```text
task-tracker/
├── backend/
│   ├── __init__.py
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       └── data/
│           └── .gitkeep
├── .gitignore
├── README.md
└── requirements.txt
```

## Requirements

Python 3.10+ is recommended.

Run all commands from the project root:

```text
task-tracker/
```

## Setup

Create a virtual environment.

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies.

```bash
pip install -r requirements.txt
```

## Run the server

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will run at:

```text
http://127.0.0.1:8000
```

## Health check

Test the `/health` endpoint:

```bash
curl http://127.0.0.1:8000/health
```

Expected response shape:

```json
{
  "status": "ok",
  "timestamp": "2026-07-07T10:30:00.000000+00:00"
}
```

The exact timestamp value will change every time you call the endpoint.

The endpoint should return HTTP 200.

## Swagger documentation

Open Swagger UI in your browser:

```text
http://127.0.0.1:8000/docs
```