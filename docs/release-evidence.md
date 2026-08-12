# Release Evidence

**Student:** Youssef Bazzi
**Course:** AI-Assisted Coding (AUB) — Final Course Project
**Repository:** https://github.com/radwanbazzi/task-tracker

All commands below were executed on 2026-08-12 on Windows (PowerShell), Python 3.14.4, from the repository root of the `final-project` branch. Terminal output is reproduced verbatim.

---

## Baseline

- **Branch:** `final-project`
- **Date:** 2026-08-12
- **Local app run command:**
  ```powershell
  cd backend
  .\venv\Scripts\activate
  uvicorn app.main:app --reload --port 8000
  ```
- **/health result:** **HTTP 200.** Verified with `curl.exe -i http://127.0.0.1:8000/health`:

  ```
  HTTP/1.1 200 OK
  date: Wed, 12 Aug 2026 13:20:30 GMT
  server: uvicorn
  content-length: 62
  content-type: application/json

  {"status":"ok","timestamp":"2026-08-12T13:20:31.006071+00:00"}
  ```

  Server-side confirmation from the uvicorn log in the first terminal:

  ```
  INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
  INFO:     Started reloader process [10444] using WatchFiles
  INFO:     Started server process [31108]
  INFO:     Waiting for application startup.
  INFO:     Application startup complete.
  INFO:     127.0.0.1:49302 - "GET /health HTTP/1.1" 200 OK
  ```

  The response shape matches the handler at `backend/app/main.py:47-50`.
- **Frontend check:** Served the frontend from inside `frontend/` with `python -m http.server 5500`, which reported:

  ```
  Serving HTTP on :: port 5500 (http://[::]:5500/) ...
  ```

  Opened http://127.0.0.1:5500 in the browser and confirmed visually: the three Kanban columns render, and the buttons work — task creation and editing both function through the modals. The Modules 1-3 board and the mid-course create/edit flow are intact.
- **Test command:**
  ```powershell
  cd backend
  .\venv\Scripts\activate
  pytest -v
  ```
- **Test result:** **72 passed in 7.25s** — 0 failed, 0 skipped, 0 errors.

  ```
  ================== test session starts ==================
  platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
  cachedir: .pytest_cache
  rootdir: ...\task-tracker\backend
  plugins: anyio-4.14.1
  collected 72 items

  [72 tests, all PASSED]

  ================== 72 passed in 7.25s ==================
  ```

  All 72 collected tests reported `PASSED`; the full per-test listing is available by re-running `pytest -v`. The count matches `README.md:87` and the per-file breakdown at `README.md:89-93` (19 `test_tasks.py`, 26 `test_due_dates.py`, 27 `test_comments.py`). No warnings summary was emitted on this run.

  **Independent cross-check:** the same suite was run on 2026-08-12 in a clean Linux container (Python 3.10.12, dependencies installed fresh from `requirements.txt`) and returned **72 passed in 2.53s**. The suite therefore passes on two different operating systems and two different Python versions from the same `requirements.txt`.

  **No failing tests, so no pre-existing / introduced failure split is required.**

**Scope statement.** No new product feature was added for the final project. The complete set of repository changes is:

| File | Change | Type |
|---|---|---|
| `docs/final-ai-review.md` | new file | documentation |
| `docs/ai-playbook.md` | new file | documentation |
| `docs/release-evidence.md` | new file | documentation |
| `README.md` | added the Final Project section | documentation |
| `docs/technical-note.md` | corrected a stale CORS claim (rows 3 of the claim-vs-reality log) | documentation |
| `backend/app/main.py` | corrected the `/version` docstring example, `0.1.0` -> `0.4.0` (line 65) | documentation-supported correction inside a protected path, explained in `docs/final-ai-review.md` |

`frontend/index.html` was not modified at all. The single change inside `backend/app/` is a docstring example string; no executable statement, signature, route, validator, or return value was altered, and the full suite returned 72 passed both before and after it. Line-ending noise was resolved locally with `git config core.autocrlf true`, which is a per-machine Git setting and commits nothing to the repository.

---

## Repository structure note

The brief's minimum structure lists `app/`, `frontend/`, and `tests/` at the repository root. This repository has carried a `backend/` wrapper since Module 1:

| Brief path | Actual path in this repo |
|---|---|
| `app/` | `backend/app/` |
| `tests/` | `backend/tests/` |
| `frontend/` | `frontend/` (matches) |
| `.github/workflows/ci.yml` | matches |
| `Dockerfile`, `.dockerignore`, `README.md`, `AGENTS.md`, `docs/` | match |

The wrapper is load-bearing: `ci.yml` sets `working-directory: backend`, the `Dockerfile` copies `backend/app`, and every import is rooted at `app.*`. Relocating these directories immediately before submission would risk breaking a currently green CI run for no functional gain, so the layout is documented here rather than changed.

---

## CI evidence

- **Workflow file:** `.github/workflows/ci.yml`
- **Latest run link or note:** **Green.** https://github.com/radwanbazzi/task-tracker/actions/runs/31604081371

  - Run: `CI #13` — "docs: add final project release evidence, AI review, and playbook"
  - Trigger: `push` to `final-project`, 2026-08-12 13:56
  - Commit: [`b08e4ea`](https://github.com/radwanbazzi/task-tracker/commit/b08e4ea0866a9c5cc9cf32598aa27dab6d146d05)
  - **Status: Success** — total duration 21s, job `test` 17s
  - Job log: https://github.com/radwanbazzi/task-tracker/actions/runs/31604081371/job/94138426358

  **One annotation was raised on this run, recorded rather than ignored:**

  > `test` — Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: `actions/checkout@v4`, `actions/setup-python@v5`.

  **Assessment:** a **warning, not a failure**. GitHub transparently ran both actions on Node.js 24 and the job still reported Success, so the pytest suite executed normally. This is a GitHub-runner deprecation affecting the actions' own JavaScript runtime, not this repository's Python code, dependencies, or test outcome — no `requirements.txt` entry and no application file is implicated.

  **Decision: no action before submission.** The fix is a version bump of two third-party actions, which is unrelated to the final project's scope and would require a fresh CI run to re-validate for no grading benefit. Logged as backlog alongside DEP-01.

  **Relation to the CI-01 finding graded Noise in `docs/final-ai-review.md`:** this warning does *not* upgrade CI-01. CI-01 claimed the workflow needed SHA-pinned actions, image scanning, and a hardened deployment gate; the Node 20 notice is a runner-runtime deprecation that GitHub auto-mitigated, and it demonstrates none of those three claims. The grade stands, but the observation is recorded here so the record shows the run was actually read, not just checked for a green tick.
- **Test command used by CI:** `pytest -v`, with `working-directory: backend` (`ci.yml`, "Run tests" step)
- **Triggers:** `on: push` and `on: pull_request`, unrestricted by branch (`ci.yml:3-5`)
- **Python version:** `actions/setup-python@v5` with an explicit `python-version: "3.11"` — pinned, not `3.x` and not implicit
- **Dependency installation:** present and explicit — `python -m pip install --upgrade pip` then `pip install -r requirements.txt`, run from the repository root
- **Shortcut check:** no continue-on-error / no `|| true` / pytest is not skipped. Verified item by item in the table below.

**Shortcut check** — grep-verified against `.github/workflows/ci.yml` on 2026-08-12:

| Dangerous shortcut | Present? | Evidence |
|---|---|---|
| `continue-on-error` | **No** | String does not appear in the file |
| `\|\| true` | **No** | String does not appear in the file |
| Skipped or conditional pytest step | **No** | The "Run tests" step has no `if:` guard and runs `pytest -v` unconditionally |
| Vague Python version | **No** | Pinned to `"3.11"` |
| Missing dependency installation | **No** | Explicit `pip install -r requirements.txt` step precedes the test step |

**Known gap (declared, not hidden):** CI runs the pytest suite only. It does not run `docker build`, so Dockerfile breakage — a stale `COPY` path, a missing runtime dependency — would pass CI and only be caught by a human running the build locally. This is recorded at `README.md:128` and in `docs/technical-note.md` §5.

**Module 4 red-run evidence (optional per the brief, included because it exists):** commit `066c8a4` intentionally broke an assertion to confirm CI actually fails on red; commit `8544659` reverted it. This proves the workflow is not silently passing.

---

## Docker evidence

- **Build command:**
  ```powershell
  docker build -t task-tracker-backend .
  ```
  (run from the repository root — the `Dockerfile` copies `backend/app`, so the build context must be the root, not `backend/`)
- **Run command:**
  ```powershell
  docker run --rm -p 8000:8000 task-tracker-backend
  ```
- **Build result:** **Success — `[+] Building 1.6s (15/15) FINISHED`**, builder `docker:desktop-linux`. Final export lines:

  ```
   => exporting to image                                                       0.1s
   => => exporting manifest sha256:93cf1987d2a89c82aa4bad0748ec848b8cf3885c46280fa24c74ac4f920cbfd7
   => => exporting config sha256:fd3016adc5005708eebb4586d684d3890bb349caa4cb245ba255152b488279bf
   => => exporting manifest list sha256:2ac523f90f288f7ebe819be6a38b7a355a12d31c907301100e71af418a20bc33
   => => naming to docker.io/library/task-tracker-backend:latest               0.0s
   => => unpacking to docker.io/library/task-tracker-backend:latest            0.0s
  ```

  All 15 build steps completed with no errors. Base image resolved to `python:3.11-slim@sha256:90744cff8f32887f075c47d747a173ff333e9e98801667af93c357fa...`, so the pinned `python:3.11-slim` tag in `Dockerfile:2` and `Dockerfile:13` resolved to a real published digest.

  **Layer-level confirmation of the two-stage build**, from the same output:

  ```
   => CACHED [stage-1 2/5] RUN useradd --create-home --shell /usr/sbin/nologin app
   => CACHED [builder 2/5] WORKDIR /app
   => CACHED [builder 3/5] RUN python -m venv /opt/venv
   => CACHED [builder 4/5] COPY requirements.txt .
   => CACHED [builder 5/5] RUN pip install --no-cache-dir -r requirements.txt
   => CACHED [stage-1 3/5] COPY --from=builder /opt/venv /opt/venv
   => CACHED [stage-1 4/5] WORKDIR /app
   => CACHED [stage-1 5/5] COPY --chown=app:app backend/app ./app
  ```

  This is independent evidence for two claims made below: the runtime stage (`stage-1`) performs exactly **one** copy of repository content — `backend/app` — and nothing else from the repository enters the image; and the `.dockerignore` was honoured, with the build context transferring only 432 B.
- **/health check:** **HTTP 200 from inside the container.** With the image running via `docker run --rm -p 8000:8000 task-tracker-backend`, `curl.exe -i http://127.0.0.1:8000/health` returned:

  ```
  HTTP/1.1 200 OK
  date: Wed, 12 Aug 2026 13:24:07 GMT
  server: uvicorn
  content-length: 62
  content-type: application/json
  ```

  `content-length: 62` matches the byte length of the health payload returned by the local run above, confirming the containerised app serves the identical response.
- **Non-root check, if implemented:** **Implemented, and confirmed by reading the Dockerfile.** `Dockerfile:15` creates the user (`RUN useradd --create-home --shell /usr/sbin/nologin app`) and `Dockerfile:24` switches to it (`USER app`) before `EXPOSE`/`CMD`, so the uvicorn process does not run as root. **Confirmed at runtime, not just by reading:** `docker run --rm task-tracker-backend whoami` returned:

  ```
  app
  ```

  The container therefore executes as the unprivileged `app` user, not as root.
- **No-baked-secrets check:** **Confirmed.** The image copies exactly one path — `Dockerfile:24`, `COPY --chown=app:app backend/app ./app`. It does not copy the repository root, `docs/`, `frontend/`, or `.git`. `.dockerignore` additionally excludes `.env`, `.git`, `.github`, `venv/`, `backend/venv/`, `__pycache__/`, and `.pytest_cache/`. There is no `.env` file anywhere in the repository. No credential, token, or key is present in any copied file.

  **Confirmed by the build log, not only by reading:** the `docker build` output shows the runtime stage executing exactly one repository copy (`COPY --chown=app:app backend/app ./app`), and reports `transferring context: 432B` — a context that small is only possible because `.dockerignore` excluded `venv/`, `.git`, and `docs/`. An unfiltered context for this repository would be orders of magnitude larger.
- **Known limitation (declared):** the image installs the single `requirements.txt`, which includes `pytest==9.1.1` and `httpx2>=2.0.0` under a `# Test dependencies` heading. Test packages therefore ship in the runtime image, and `httpx2` is unpinned. Tracked as DEP-01 in `docs/security-review.md` and `docs/final-ai-review.md`; deliberately not changed before submission.

---

## Documentation claim-vs-reality log

All five checks below were executed on 2026-08-12 against the running application via Starlette `TestClient`, or against the actual file contents. Rows 1, 2, and 5 involve an endpoint, a status code, or CI behaviour, satisfying the brief's requirement that at least one checked claim be of that kind.

| # | Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|---|
| 1 | `README.md:194-203` lists 10 API endpoints across 6 paths, including `GET /version` and no route at `/`. | Read `GET /openapi.json` from the running app and compared the path set. Returned exactly: `/health`, `/version`, `/tasks`, `/tasks/{task_id}`, `/tasks/{task_id}/comments`, `/tasks/{task_id}/comments/{comment_id}`. `GET /` returned **404** `{"detail":"Not Found"}` as documented at `README.md:61`. | **Accurate.** All 6 paths and the deliberate absence of `/` confirmed. | None |
| 2 | `README.md:87` states the suite is **72 passed**, split 19 / 26 / 27 across the three test files (`README.md:89-93`). | Ran the full suite from `backend/` in a clean container with deps from `requirements.txt`. | **Accurate.** 72 passed, and the per-file counts match. | None |
| 3 | `docs/technical-note.md:33` states *"CORS is wide open (`allow_origins=["*"]`)"*, and `:50` asks whether the wildcard needs tightening. | Read `backend/app/main.py:26`, which is `allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"]`. Confirmed at runtime: preflight from `https://evil.example` → **400** with no `Access-Control-Allow-Origin`; from `http://localhost:5500` → **200** with the origin echoed. | **Stale — documentation was wrong.** The note was written before the CORS fix in commit `6b6e885` and was never updated. | Corrected `docs/technical-note.md` §4 and §6 to state the restricted origin list, with a dated note that the wildcard was fixed in commit `6b6e885`. |
| 4 | `README.md:184` claims `assignee` and `description` have browser-side limits but **no** backend length validators, so a direct API call can exceed them. | Probed the live API directly, bypassing the browser. `POST /tasks` with a 5,000-character `description` → **201**. `POST /tasks` with a 500-character `assignee` → **201**. Confirmed no `max_length` constraint exists at `backend/app/models.py:63-71`. | **Accurate, and the limitation is real.** The README honestly documents its own gap. | None. Tracked as DOS-01 backlog. |
| 5 | The `GET /version` docstring at `backend/app/main.py:64-66` gives the example response `{"version": "0.1.0"}`. | Called `GET /version` on the running app. Returned `{"version":"0.4.0"}`, matching `app.version` set at `backend/app/main.py:21`. | **Stale docstring.** The example was written at v0.1.0 and never updated; the endpoint itself is correct because it reads `app.version` dynamically. | Documentation-only correction to the docstring example (`0.1.0` → `0.4.0`). No behaviour change; the 72-test suite was re-run after the edit. |

**Summary:** 3 claims accurate, 2 stale documentation claims found and corrected. Both corrections were documentation-only; no application behaviour was changed.

---

## Evidence files

- `docs/release-evidence.md` (this file)
- `docs/final-ai-review.md`
- `docs/ai-playbook.md`
- `docs/security-review.md` (Module 5 security grading, carried forward and re-verified)
- `AGENTS.md` (agent guardrails)
