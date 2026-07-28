# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. Tech stack

- **Python** 3.11 or newer (developed on 3.14; see `README.md`)
- **FastAPI** 0.139.0 — web framework (`requirements.txt`)
- **Pydantic** v2, 2.13.4 — request/response schemas, `extra="forbid"` on inputs (`requirements.txt`)
- **Uvicorn** 0.51.0 (`[standard]` extras) — ASGI server (`requirements.txt`)
- **pytest** 9.1.1 — test runner (`requirements.txt`)
- **httpx** — used via Starlette's `TestClient` for API tests. `requirements.txt` pins this as `httpx2>=2.0.0` — `[VERIFY]` this looks like it may be a typo for `httpx`, but that is what the file currently says, so it is reported as-is rather than corrected.
- **Frontend**: vanilla JavaScript + inline CSS in a single static `index.html` (no framework, no build step)

## 2. Run command

Exact command used in this course (from `backend/`, venv activated):

```powershell
uvicorn app.main:app --reload --port 8000
```

**Activate venv first (Windows PowerShell):**
```powershell
cd backend
.\venv\Scripts\activate
```

**Run the frontend** (separate terminal, from `frontend/` — must be served from inside this folder, not the repo root):
```powershell
python -m http.server 5500
```
Frontend: `http://127.0.0.1:5500`. Backend: `http://127.0.0.1:8000` (no route at `/`; use `/docs` or `/health`).

## 3. Test command

Exact command used in this course (from `backend/`, venv activated):

```powershell
pytest -v
```

**Run a single test file:**
```powershell
pytest tests/test_tasks.py -v
pytest tests/test_due_dates.py -v
pytest tests/test_comments.py -v
```

**Run a single test by name:**
```powershell
pytest tests/test_tasks.py::test_name -v
```

Expected result: **72 passed** across all three test files (19 + 26 + 27, per `README.md`).

## 4. Architecture summary

**Backend** — single-file FastAPI app (`backend/app/main.py`) with four supporting modules:

- **`main.py`** — FastAPI app, CORS middleware, and all route handlers (`/health`, `/tasks`, `/tasks/{id}`, `/tasks/{id}/comments`, `/tasks/{id}/comments/{comment_id}`).
- **`models.py`** — Pydantic v2 schemas. `TaskCreate`/`TaskUpdate` use `extra="forbid"` so unknown fields (including `is_overdue` and `comment_count`) are rejected with 422. `TaskResponse` holds the derived fields.
- **`storage.py`** — Pure in-memory dicts (`_tasks`, `_comments`). No persistence. `_reset()` is called by test fixtures before/after each test. Cascade delete of comments is handled inside `delete_task`.
- **`business_rules.py`** — Status transition guard (task rules live here — see Section 5).
- **`task_rules.py`** — `build_task_response` computes `is_overdue` and injects `comment_count` into a `TaskResponse` copy (task rules live here too — see Section 5).

**Data flow for task responses:** `main.py` always calls `build_task_response(task, today=date.today(), comment_count=...)` before returning — never returns a raw stored task, because stored tasks have `is_overdue=False` and `comment_count=0` as defaults.

**Frontend** — `frontend/index.html`: a single static file containing markup, inline CSS, and vanilla JS. Talks to the backend at `http://127.0.0.1:8000` via `fetch`. Must be served from inside `frontend/`, not the repo root (see Section 2).

**Tests** — `backend/tests/`:
- `conftest.py` — wires an `autouse` fixture that calls `storage._reset()` before and after every test, so no state leaks between tests. Date-sensitive tests compute dates relative to `date.today()` at runtime, not hardcoded values.
- `test_tasks.py` — Module 1–3 task CRUD, filters, transitions (19 tests per `README.md`).
- `test_due_dates.py` — due dates, overdue, filtering (26 tests per `README.md`).
- `test_comments.py` — comments, counts, cascade delete (27 tests per `README.md`).

## 5. Business rules

**Task status values** (`app/models.py`, `TaskStatus` enum): `ToDo`, `InProgress`, `Done`.

**Status transition rules** (`app/business_rules.py`, `VALID_TRANSITIONS`) — only these transitions are valid, enforced in `main.py`'s `PATCH /tasks/{task_id}` before the update is applied:
- `ToDo → InProgress`
- `InProgress → Done`
- `Done → InProgress`

Any other transition raises `HTTPException(422)` with the allowed-transitions list in the detail message.

**Overdue rule** (`app/task_rules.py`, `compute_is_overdue`): a task's `is_overdue` is `True` when `due_date` is set, `due_date < today`, and `status` is not `Done`. This is a derived field computed on every response, never stored.

**Input validation** (`app/models.py`): `TaskCreate`/`TaskUpdate`/`CommentCreate` all use `extra="forbid"`. Title must be non-blank and ≤200 chars; comment text must be non-blank and ≤1000 chars; comment author, if provided, must be ≤50 chars after trimming (blank becomes `None`).

## 6. UI states and CORS notes

**UI states** (`frontend/index.html`):
- Loading state — `#loadingOverlay`, toggled active while a fetch is in flight.
- Error state — `#errorMessage` / `#errorText`, shown via `showErrorMessage()` on fetch failures (including non-OK HTTP responses).
- Empty state — `.empty-placeholder` rendered when a filtered task list is empty.

**CORS** (`app/main.py`): `CORSMiddleware` is configured with `allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]`. Per `README.md`, this is acceptable for local development only and is not a production configuration.

## 7. Do-not rules

Do not do any of the following without asking first:
- Add authentication or authorization.
- Add a database or any persistence layer (current storage is intentionally in-memory).
- Add deployment steps, Docker, or CI/CD configuration.
- Make major UI changes (layout, framework adoption, redesign) beyond small, scoped fixes.
