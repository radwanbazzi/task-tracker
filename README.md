# Task Tracker

A small full-stack task tracker built across Modules 1–3 of the AUB AI-Assisted Coding programme, extended for the mid-course project with two additional end-to-end features, and for Module 4 with a Dockerfile and a CI workflow.

- **Backend:** Python 3 + FastAPI + Pydantic v2, with in-memory storage
- **Frontend:** a single static `index.html` (vanilla JS Kanban board)
- **Tests:** pytest + Starlette TestClient

## 1. Project overview

**From Modules 1–3**

- Create tasks with title, description, status (ToDo / InProgress / Done), priority (Low / Medium / High), and assignee
- View tasks on a three-column Kanban board
- Filter by status and priority
- Update tasks, including drag-and-drop status changes
- Delete tasks
- Restricted status transitions: only `ToDo → InProgress`, `InProgress → Done`, and `Done → InProgress` are permitted; anything else returns HTTP 422

**Added for the mid-course project**

- **Due dates + overdue filter** — an optional `due_date` on every task, a backend-computed `is_overdue` flag, an "Overdue" pill on the card, and a "Show overdue only" filter that combines with status and priority
- **Task comments** — add, list, and delete comments on a task, with a comment count on the card and a comments panel in the edit modal; deleting a task removes its comments

**Added for Module 4**

- A `Dockerfile` that builds and runs the backend in a container
- A GitHub Actions CI workflow (`.github/workflows/ci.yml`) that runs the test suite on every push and pull request

> **Note:** storage is in memory, in both the local run and the Docker container. All tasks and comments are lost on restart. This is intentional for the scope of this project — see [Project conventions and current limitations](#9-project-conventions-and-current-limitations).

## 2. Prerequisites

- Python 3.11 or newer (developed on 3.14; see below)
- `pip`
- No database, no external services
- Docker Desktop or Docker Engine — only needed for [Run with Docker](#6-run-with-docker); everything else in this README works without it

## 3. Local setup

From the repository root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate          # Windows PowerShell
# source venv/bin/activate       # macOS / Linux
pip install -r ..\requirements.txt
```

## 4. Run the app locally

**Backend** (from the repository root, first terminal):

```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

The API runs at [http://127.0.0.1:8000](http://127.0.0.1:8000). There is no route at `/` — requesting it correctly returns `{"detail":"Not Found"}`. Use:

- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) — interactive Swagger console
- [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) — health check

**Frontend** (from the repository root, second terminal — leave the backend running in the first):

```powershell
cd frontend
python -m http.server 5500
```

Open [http://127.0.0.1:5500](http://127.0.0.1:5500).

Serve from inside the `frontend` folder, not the repository root — otherwise Python serves a directory listing of the whole project instead of the app.

## 5. Run tests

From the repository root:

```powershell
cd backend
.\venv\Scripts\activate
pytest -v
```

Expected: **72 passed**.

| File | Tests | Covers |
| :---- | ----: | :---- |
| `tests/test_tasks.py` | 19 | Modules 1–3 task CRUD, filters, transitions |
| `tests/test_due_dates.py` | 26 | Feature A — due dates, overdue, filtering |
| `tests/test_comments.py` | 27 | Feature B — comments, counts, cascade delete |

All date-dependent tests compute their dates relative to `date.today()` at run time, so the suite does not break on a future calendar day and needs no clock-mocking library.

**Run a single test file:**

```powershell
cd backend
.\venv\Scripts\activate
pytest tests/test_tasks.py -v
```

**Run a single test by name:**

```powershell
cd backend
.\venv\Scripts\activate
pytest tests/test_tasks.py::test_name -v
```

## 6. Run with Docker

The `Dockerfile` at the repository root builds a container for the **backend only** — there is no Dockerfile or docker-compose setup for the frontend, so it is still served with `python -m http.server` as in [Run the app locally](#4-run-the-app-locally). The image is a two-stage build (`python:3.11-slim`) that installs `requirements.txt` into a venv, copies in `backend/app`, and runs as a non-root `app` user.

From the repository root:

```powershell
docker build -t task-tracker-backend .
docker run --rm -p 8000:8000 task-tracker-backend
```

The API is then available at the same [http://127.0.0.1:8000](http://127.0.0.1:8000), with `/docs` and `/health` working as above. The container has no volume mount, so — same as running locally — all data is lost when the container stops.

To use the frontend against the Dockerized backend, run the frontend server from [Run the app locally](#4-run-the-app-locally) in a separate terminal. CORS permits the supported local frontend origins `http://localhost:5500` and `http://127.0.0.1:5500`.

`[VERIFY]` The CI workflow (below) does not build or run this Docker image — only `docker build`/`docker run`, tried locally, confirm the image works. **Verified 2026-08-12:** the image was built and run locally, `/health` returned HTTP 200 from inside the container, and `docker run --rm task-tracker-backend whoami` returned `app`, confirming the non-root runtime. Full output in `docs/release-evidence.md`.

## 7. CI workflow summary

`.github/workflows/ci.yml` defines one job, `test`, that runs on `push` and `pull_request` (any branch):

1. Checks out the repository (`actions/checkout@v4`)
2. Sets up Python 3.11 (`actions/setup-python@v5`)
3. Installs dependencies: `pip install -r requirements.txt`, run from the repository root
4. Runs the test suite: `pytest -v`, run with `working-directory: backend`

There is no separate lint step, no Docker build/push step, and no deployment step in this workflow — it only runs the pytest suite described in [Run tests](#5-run-tests).

## 8. Project structure

```
task-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app and all endpoints
│   │   ├── models.py          # Pydantic request/response schemas
│   │   ├── storage.py         # In-memory task and comment storage
│   │   ├── business_rules.py  # Status-transition validation
│   │   └── task_rules.py      # Derived overdue logic (date-injectable)
│   └── tests/
│       ├── conftest.py
│       ├── test_tasks.py
│       ├── test_due_dates.py
│       └── test_comments.py
├── frontend/
│   └── index.html             # Complete UI: markup, styles, and script
├── docs/
│   └── midcourse/             # Mid-course project documentation
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions: pytest on push/PR
├── Dockerfile                 # Backend-only container build
├── .dockerignore
├── requirements.txt
└── README.md
```

## 9. Project conventions and current limitations

**Conventions**

- Task responses are never returned raw from storage — `main.py` always calls `build_task_response(task, today=date.today(), comment_count=...)` first, because stored tasks default `is_overdue=False` and `comment_count=0`. See `app/task_rules.py`.
- `is_overdue` and `comment_count` are **derived**, never stored, and rejected on input: `TaskCreate`/`TaskUpdate`/`CommentCreate` all use Pydantic's `extra="forbid"`, so sending either field returns 422.
- Status transitions are restricted to `ToDo → InProgress`, `InProgress → Done`, and `Done → InProgress` (`app/business_rules.py`); any other transition returns 422 with the allowed transitions listed in the response.
- Title must be non-blank and ≤200 chars; comment text must be non-blank and ≤1000 chars; comment author, if provided, must be ≤50 chars after trimming (blank becomes `None`).
- Explicit `null` is rejected for task-update `title`, `description`, `status`, and `priority`; omitting those fields still leaves them unchanged.
- Non-string comment authors are rejected with HTTP 422 instead of causing an internal server error.

**Current limitations**

- Storage is in memory (both local and Docker); data does not survive a restart
- `assignee` and `description` have browser-side `maxlength` limits but no backend length validators, so a direct API call can exceed them
- CORS allows only `http://localhost:5500` and `http://127.0.0.1:5500`; methods and headers remain unrestricted for local development, so this is not a production configuration
- No authentication, no database, and no deployment configuration beyond the local-use Dockerfile described in [Run with Docker](#6-run-with-docker) — none of this is production-ready
- Do not expose the API beyond trusted local development; authentication and authorization are required before any network or production deployment
- `requirements.txt` leaves the test HTTP client open-ended as `httpx2>=2.0.0`. The installed Starlette warning identifies `httpx2` as its expected test-client dependency; splitting runtime/test requirements and locking versions remains backlog work

## 10. API endpoints

| Method | Path | Notes |
| :---- | :---- | :---- |
| GET | `/health` | Health check |
| GET | `/version` | Returns the running API version |
| GET | `/tasks` | Optional `status`, `priority`, `overdue` filters (AND) |
| POST | `/tasks` | 201 on success |
| GET | `/tasks/{task_id}` | 404 if missing |
| PATCH | `/tasks/{task_id}` | Partial update; 422 on invalid transition or explicit null for required task fields |
| DELETE | `/tasks/{task_id}` | 204; also deletes that task's comments |
| POST | `/tasks/{task_id}/comments` | 201; 404 if task missing |
| GET | `/tasks/{task_id}/comments` | 200; `[]` if none; 404 if task missing |
| DELETE | `/tasks/{task_id}/comments/{comment_id}` | 204; 404 if either is missing |

## 11. Decisions and mid-course project documentation

`[VERIFY]` There is no `docs/decisions/` folder in this repository. The nearest equivalent is the mini architecture decision record below, under `docs/midcourse/`.

All mid-course project documentation lives in
[docs/midcourse](https://github.com/radwanbazzi/task-tracker/tree/mid-course-project/docs/midcourse):

- [user-stories.md](https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/user-stories.md) — user stories with acceptance and failure criteria
- [mini-adr.md](https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/mini-adr.md) — architecture decision record for both features (the closest thing this repo has to `docs/decisions/`)
- [prompt-log.md](https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/prompt-log.md) — the AI prompts used, and what was accepted or rejected
- [verification.md](https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/verification.md) — baseline, test results, browser checks, Break Tests
- [reflection.md](https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/reflection.md) — reflection on the AI-assisted workflow

## 12. Final Project

Branch reviewed: `final-project`

### What this submission demonstrates

- The existing Task Tracker still runs inside the intended course scope; no new product feature was added.
- CI runs the pytest suite on every push and pull request.
- The Docker image builds and runs, with `/health` returning 200.
- AI review, security, and ownership evidence is in `docs/`.

### Repository structure note

The final-project brief lists `app/`, `frontend/`, and `tests/` at the repository root. This repo has carried a `backend/` wrapper since Module 1, so the brief's `app/` is `backend/app/` and its `tests/` is `backend/tests/`. The wrapper is load-bearing (`ci.yml` sets `working-directory: backend`, the `Dockerfile` copies `backend/app`, and all imports are rooted at `app.*`), so it is documented rather than relocated. See `docs/release-evidence.md`.

### How to run locally

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r ..\requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend, in a second terminal:

```powershell
cd frontend
python -m http.server 5500
```

Open http://127.0.0.1:5500. The API is at http://127.0.0.1:8000 (`/docs`, `/health`, `/version`; there is no route at `/`).

### How to run tests

```powershell
cd backend
.\venv\Scripts\activate
pytest -v
```

Expected: **72 passed**.

### How to run with Docker

From the repository root:

```powershell
docker build -t task-tracker-backend .
docker run --rm -p 8000:8000 task-tracker-backend
curl.exe -i http://127.0.0.1:8000/health
```

Expected: HTTP `200` with `{"status":"ok","timestamp":"..."}`.

### Evidence files

- `docs/release-evidence.md` — baseline, CI, Docker, and claim-vs-reality evidence
- `docs/final-ai-review.md` — AI code review mini-log, security mini-review, manual check, ownership statement
- `docs/ai-playbook.md` — personal AI playbook and decision card
- `docs/security-review.md` — Module 5 security grading, carried forward and re-verified
- `AGENTS.md` — agent guardrails

### AI assistance summary

AI helped draft or review: CI workflow, Dockerfile, test scaffolding, the security review, the code review pass, and documentation.

I verified the work by: running the full `pytest -v` suite (72 passed), probing endpoints directly with Starlette `TestClient` (`/health`, `/version`, CORS preflight, oversized payloads, null and non-string inputs), reviewing each diff with `git show`, building and running the Docker container and checking `/health`, and manually tracing every `innerHTML` sink in `frontend/index.html`.

One AI suggestion I rejected or corrected: an AI review comment claimed commit `772e335` broke `TaskUpdate`'s partial-update contract by rejecting omitted fields. I disproved it by running `PATCH /tasks/{id}` with only `status` set (returned 200) and confirming the two tests that encode that contract still pass. No change was made, and the comment is recorded as **Wrong** in `docs/final-ai-review.md`.
