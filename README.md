# Task Tracker

A small full-stack task tracker built across Modules 1–3 of the AUB AI-Assisted Coding programme, extended for the mid-course project with two additional end-to-end features.

- **Backend:** Python 3 \+ FastAPI \+ Pydantic v2, with in-memory storage  
- **Frontend:** a single static `index.html` (vanilla JS Kanban board)  
- **Tests:** pytest \+ Starlette TestClient

## Features

**From Modules 1–3**

- Create tasks with title, description, status (ToDo / InProgress / Done), priority (Low / Medium / High), and assignee  
- View tasks on a three-column Kanban board  
- Filter by status and priority  
- Update tasks, including drag-and-drop status changes  
- Delete tasks  
- Restricted status transitions: only `ToDo → InProgress`, `InProgress → Done`, and `Done → InProgress` are permitted; anything else returns HTTP 422

**Added for the mid-course project**

- **Due dates \+ overdue filter** — an optional `due_date` on every task, a backend-computed `is_overdue` flag, an "Overdue" pill on the card, and a "Show overdue only" filter that combines with status and priority  
- **Task comments** — add, list, and delete comments on a task, with a comment count on the card and a comments panel in the edit modal; deleting a task removes its comments

## Requirements

- Python 3.11 or newer (developed on 3.14)  
- No database, no Docker, no external services

>   
> **Note:** storage is in memory. All tasks and comments are lost when the backend restarts. This is intentional for the scope of this project.

## Setup

From the repository root:

cd backend

python \-m venv venv

.\\venv\\Scripts\\activate          \# Windows PowerShell

\# source venv/bin/activate       \# macOS / Linux

pip install \-r ..\\requirements.txt

## Running the backend

cd backend

.\\venv\\Scripts\\activate

uvicorn app.main:app \--reload

The API runs at [**http://127.0.0.1:8000**](http://127.0.0.1:8000).

There is no route at `/` — requesting it correctly returns `{"detail":"Not Found"}`. Use:

- [**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs) — interactive Swagger console  
- [**http://127.0.0.1:8000/health**](http://127.0.0.1:8000/health) — health check

## Opening the frontend

The frontend is a static file and needs its own server, in a **second** terminal (leave the backend running in the first):

cd frontend

python \-m http.server 5500

Open [**http://127.0.0.1:5500**](http://127.0.0.1:5500).

Serve from inside the `frontend` folder, not the repository root — otherwise Python serves a directory listing of the whole project instead of the app.

## Running the tests

cd backend

.\\venv\\Scripts\\activate

pytest \-v

Expected: **72 passed**.

| File | Tests | Covers |
| :---- | ----: | :---- |
| `tests/test_tasks.py` | 19 | Modules 1–3 task CRUD, filters, transitions |
| `tests/test_due_dates.py` | 26 | Feature A — due dates, overdue, filtering |
| `tests/test_comments.py` | 27 | Feature B — comments, counts, cascade delete |

All date-dependent tests compute their dates relative to `date.today()` at run time, so the suite does not break on a future calendar day and needs no clock-mocking library.

## API endpoints

| Method | Path | Notes |
| :---- | :---- | :---- |
| GET | `/health` | Health check |
| GET | `/tasks` | Optional `status`, `priority`, `overdue` filters (AND) |
| POST | `/tasks` | 201 on success |
| GET | `/tasks/{task_id}` | 404 if missing |
| PATCH | `/tasks/{task_id}` | Partial update; 422 on invalid transition |
| DELETE | `/tasks/{task_id}` | 204; also deletes that task's comments |
| POST | `/tasks/{task_id}/comments` | 201; 404 if task missing |
| GET | `/tasks/{task_id}/comments` | 200; `[]` if none; 404 if task missing |
| DELETE | `/tasks/{task_id}/comments/{comment_id}` | 204; 404 if either is missing |

`is_overdue` and `comment_count` are **derived** response fields. They are never stored and are rejected on input — request models use `extra="forbid"`, so sending either returns 422\.

## Project structure

task-tracker/

├── backend/

│   ├── app/

│   │   ├── main.py            \# FastAPI app and all endpoints

│   │   ├── models.py          \# Pydantic request/response schemas

│   │   ├── storage.py         \# In-memory task and comment storage

│   │   ├── business\_rules.py  \# Status-transition validation

│   │   └── task\_rules.py      \# Derived overdue logic (date-injectable)

│   └── tests/

│       ├── conftest.py

│       ├── test\_tasks.py

│       ├── test\_due\_dates.py

│       └── test\_comments.py

├── frontend/

│   └── index.html             \# Complete UI: markup, styles, and script

├── docs/

│   └── midcourse/             \# Mid-course project documentation

├── requirements.txt

└── README.md

## Mid-course project documentation

See [`docs/midcourse/`](http://docs/midcourse/):

- `user-stories.md` — user stories with acceptance and failure criteria  
- `mini-adr.md` — architecture decision record for both features  
- `prompt-log.md` — the AI prompts used, and what was accepted or rejected  
- `verification.md` — baseline, test results, browser checks, Break Tests  
- `reflection.md` — reflection on the AI-assisted workflow

## Known limitations

- Storage is in memory; data does not survive a restart  
- `assignee` and `description` have browser-side `maxlength` limits but no backend length validators, so a direct API call can exceed them  
- CORS is set to `allow_origins=["*"]`, which is acceptable for local development only

