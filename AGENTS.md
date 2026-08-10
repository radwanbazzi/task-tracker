# AGENTS.md

## Purpose and scope

This file provides repository-wide guidance for Codex and other coding agents working on the Task Tracker.

Use repository evidence as the source of truth. Cite the relevant file when reporting a command, rule, behavior, or finding. If evidence is missing or conflicting, label the item `not confirmed` instead of guessing.

## Project summary

Task Tracker is a small full-stack Kanban application developed through Modules 1–4 of the AUB AI-Assisted Coding programme. Module 5 adds agent workflow and governance guidance; it does not by itself authorize application changes.

The application supports task CRUD, status and priority filtering, restricted status transitions, due dates and overdue filtering, and task comments.

Architecture:

- `backend/app/main.py`: FastAPI application, middleware, and HTTP routes.
- `backend/app/models.py`: Pydantic request and response schemas.
- `backend/app/storage.py`: module-level in-memory task and comment storage.
- `backend/app/business_rules.py`: allowed task status transitions.
- `backend/app/task_rules.py`: derived overdue and comment-count fields.
- `backend/tests/`: pytest API and business-rule tests.
- `frontend/index.html`: complete static frontend using HTML, inline CSS, and vanilla JavaScript.
- `docs/midcourse/`: user stories, decisions, verification notes, prompt log, and reflection.
- `docs/security-review.md`: Module 5 security grading, resolution status, and deferred backlog items.

Storage is intentionally in memory. Tasks and comments do not survive an application restart.

## Tech stack

Confirmed from `requirements.txt`, `Dockerfile`, `.github/workflows/ci.yml`, and `frontend/index.html`:

- Python 3.11 or newer; Docker and CI use Python 3.11.
- FastAPI 0.139.0.
- Pydantic 2.13.4.
- Uvicorn 0.51.0 with standard extras.
- pytest 9.1.1.
- Starlette `TestClient` for API tests.
- Static HTML, inline CSS, and vanilla JavaScript; no frontend framework or build step.
- Docker backend image using `python:3.11-slim`.
- GitHub Actions runs pytest on pushes and pull requests.

Dependency caveat: `requirements.txt` contains the open-ended test dependency `httpx2>=2.0.0`. The installed Starlette warning identifies `httpx2` as its expected test-client dependency. Do not silently replace it with `httpx`; splitting runtime/test requirements and locking versions remains backlog work.

## Supported setup, run, and test commands

Run commands from the repository root unless a command says otherwise.

### Local setup

Documented in `README.md`; a fresh installation was not executed while drafting this file:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r ..\requirements.txt
```

A fresh dependency installation is not confirmed. The current environment runs the suite with `httpx2`, but its open-ended version range remains a reproducibility limitation.

### Backend

From `backend/` with the virtual environment activated:

```powershell
uvicorn app.main:app --reload --port 8000
```

The API is served at `http://127.0.0.1:8000`. Use `/docs`, `/health`, or `/version`; no root `/` route is defined.

### Frontend

In a separate terminal:

```powershell
cd frontend
python -m http.server 5500
```

Open `http://127.0.0.1:5500`. Serve from `frontend/`, not the repository root. The frontend calls the backend at `http://localhost:8000`.

### Tests

From `backend/` with the virtual environment activated:

```powershell
pytest -v
```

There are 72 test functions across the three main test files. The full suite was last confirmed during the Module 5 security fixes with `pytest -q -p no:cacheprovider`: 72 passed with one Starlette `httpx`/`httpx2` deprecation warning.

Single-file examples:

```powershell
pytest tests/test_tasks.py -v
pytest tests/test_due_dates.py -v
pytest tests/test_comments.py -v
```

Single-test example:

```powershell
pytest tests/test_tasks.py::test_name -v
```

### Docker backend

From the repository root:

```powershell
docker build -t task-tracker-backend .
docker run --rm -p 8000:8000 task-tracker-backend
```

The Dockerfile packages the backend only. A Docker build was not run while drafting this file.

No lint, formatter, type-check, frontend-test, frontend-build, deployment, or Docker Compose command is confirmed by the repository.

## Business rules

### Tasks

Sources: `backend/app/models.py`, `backend/app/main.py`, `backend/app/storage.py`, and `backend/tests/test_tasks.py`.

- Status values are exactly `ToDo`, `InProgress`, and `Done`.
- Priority values are exactly `Low`, `Medium`, and `High`.
- New tasks default to status `ToDo`, priority `Medium`, an empty description, no assignee, and no due date.
- A title is required when creating a task. A supplied title is trimmed, cannot be blank, and cannot exceed 200 characters.
- Task updates are partial: omitted fields remain unchanged.
- Explicit `null` for task-update `title`, `description`, `status`, or `priority` is rejected with HTTP 422. `assignee` and `due_date` remain nullable.
- Unknown input fields are rejected with HTTP 422 because input models use `extra="forbid"`.
- Status, priority, and overdue filters are combined using AND logic.
- Backend length validation for task descriptions and assignees is not present. The frontend limits them to 2,000 and 50 characters respectively, but those are not API validation rules.

### Status transitions

Source: `backend/app/business_rules.py`.

Only these status transitions are allowed:

- `ToDo -> InProgress`
- `InProgress -> Done`
- `Done -> InProgress`

All other transitions, including setting the current status again, return HTTP 422.

### Due dates and overdue state

Sources: `backend/app/models.py`, `backend/app/task_rules.py`, and `backend/tests/test_due_dates.py`.

- `due_date` is optional.
- An empty-string due date is normalized to `None`.
- Invalid calendar dates, booleans, and integers are rejected.
- `is_overdue` is true only when a due date exists, the due date is earlier than today, and the task is not `Done`.
- A task due today is not overdue.
- `is_overdue` is computed for responses and is never accepted as client input.

### Comments

Sources: `backend/app/models.py`, `backend/app/storage.py`, and `backend/tests/test_comments.py`.

- Comment text is required, trimmed, non-blank, and at most 1,000 characters.
- Comment author is optional, trimmed, and at most 50 characters. A blank author becomes `None`; non-string authors are rejected with HTTP 422.
- Comments are returned in insertion order, oldest first.
- `comment_count` is derived for task responses and is not accepted as client input.
- Deleting a task also deletes its comments.
- A comment can only be deleted through the task to which it belongs.

### Storage and deployment limits

Sources: `backend/app/storage.py`, `backend/app/main.py`, and `README.md`.

- Storage uses module-level dictionaries and is not persistent.
- Tests reset storage before and after every test.
- There is no authentication or authorization.
- CORS permits only `http://localhost:5500` and `http://127.0.0.1:5500`; methods and headers remain unrestricted for local development. This is not production configuration.
- Do not expose the API beyond trusted local development; authentication and authorization are required before network or production deployment.
- No database or production deployment configuration is present.

## Module 5 guardrails

- **Docs first:** Read `README.md`, relevant files under `docs/`, and applicable tests before proposing code changes. For behavior changes, establish or update the expected behavior and acceptance criteria before editing application code.
- **Read-only by default:** Begin with inspection and analysis. A request to review, explain, diagnose, or draft does not authorize file changes, dependency installation, server startup, or external actions.
- **One task per thread:** Keep each Codex task focused on one clearly defined objective. Route unrelated work to a separate task instead of combining scopes.
- **No application changes without approval:** Do not modify `backend/app/` unless the user explicitly approves application-code changes in the current task. Treat `frontend/index.html` as application code and ask before modifying it as well.
- Approval to inspect, review, document, or suggest a change is not approval to implement it.
- Do not broaden the requested scope. If a necessary change falls outside the approved files or objective, stop and request approval.

## Security and governance

- Never paste, expose, commit, or repeat passwords, tokens, API keys, credentials, `.env` contents, or other secrets. Redact sensitive values and report only the affected file or setting.
- Do not run destructive commands. This includes deleting broad paths, clearing data, force-resetting Git state, or overwriting user work.
- Inspect `git status` before approved edits and preserve unrelated or pre-existing changes.
- Cite repository-relative file paths, and line numbers where practical, for findings and behavioral claims.
- For AI-Assisted Coding – Module 5 Prompt Library work, report only findings supported by repository evidence.
- Never invent test results, vulnerabilities, approvals, commands, business rules, file contents, or completed actions.
- Distinguish clearly between:
  - **Confirmed:** directly supported by inspected code, tests, configuration, documentation, or executed verification.
  - **Inference:** a conclusion drawn from confirmed evidence; label it as an inference.
  - **Not confirmed:** evidence is absent, conflicting, or has not been executed.
- When approved code changes are made, run the narrowest relevant tests first, then the full `pytest -v` suite when appropriate. Report the actual command and result rather than claiming success from inspection alone.
