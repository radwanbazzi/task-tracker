Technical Decision Note: Architecture Choice for the Task Tracker (Module 4)
Status: Draft
Scope: Backend architecture (single-file FastAPI + Pydantic + in-memory storage), plus Module 4 additions (Dockerfile, CI workflow)

1. Context
The Task Tracker is a small full-stack app built incrementally across Modules 1–4 of the AUB AI-Assisted Coding programme:

Backend: a single FastAPI app (backend/app/main.py) with route handlers for tasks (/tasks, /tasks/{id}) and comments (/tasks/{id}/comments, /tasks/{id}/comments/{comment_id}), backed by four supporting modules — models.py (Pydantic v2 schemas), storage.py (in-memory dicts), business_rules.py (status-transition guard), and task_rules.py (derived-field computation).
Storage: pure in-memory (_tasks, _comments dicts in storage.py). No database. Data does not survive a process restart, in either the local run or the Docker container.
Frontend: a single static index.html (vanilla JS + inline CSS, no build step), served separately via python -m http.server.
Tests: pytest + Starlette TestClient, 72 tests across three files.
Module 4 additions: a two-stage Dockerfile (builds a venv, copies in backend/app, runs as a non-root user) that containerizes the backend only, and a GitHub Actions workflow (.github/workflows/ci.yml) that runs pytest -v on every push/PR. Per CLAUDE.md, these were an explicitly approved exception to the project's normal "no Docker/CI without asking" rule.
There is no authentication, no database, and no deployment configuration — this is a local-development, course-scoped project, not a production system.
This note exists now because Module 4 added Docker and CI on top of an already-settled backend architecture, raising the question of whether to extend further (persistence, auth, deployment) — the sections below record why the answer is no, for this course scope.

2. Decision
Keep the backend as a single-file FastAPI app with in-memory storage, split only along four thin modules (routes, schemas, storage, business rules), with no ORM, no database, and no persistence layer. Containerize the backend with a two-stage Docker build that produces a minimal, non-root runtime image, and run the existing pytest suite in GitHub Actions on every push and pull request as the only CI gate. The frontend stays a single static HTML file with no framework and no build step, served independently of the backend and of Docker.

This is the architecture going forward for the current course scope. It is not a placeholder for a "real" backend — it is deliberately sized to the project's requirements (CRUD + derived fields + status rules), and the Docker/CI additions exist to demonstrate containerization and automated testing, not to stand up a deployment pipeline.

3. Alternatives Considered
Split into a multi-package/service backend (e.g., separate routers/, services/, repositories/ layers). Rejected: the app has four route groups and one storage model; the current four-module split (main.py, models.py, storage.py, business_rules.py/task_rules.py) already isolates concerns without the overhead of a layered architecture nobody needs yet.
Add a real database (SQLite/Postgres via an ORM). Rejected per the project's explicit do-not-rule (CLAUDE.md §7): no persistence layer without asking. In-memory storage is sufficient for course grading and local demos, and it keeps storage._reset() — the mechanism the test suite relies on for isolation — simple.
Skip Docker/CI entirely (staying strictly within the original do-not-rules). Rejected because the user explicitly approved both as a Module 4 exception (CLAUDE.md, "Exception on record").
Have CI also build/run the Docker image, not just pytest. Not adopted: README.md §7 and [VERIFY] note in §6 both record that CI currently only runs the test suite; the Docker image has only been verified with a local docker build/docker run, not in the pipeline.
Deploy the container somewhere (a cloud run target, docker-compose with a frontend service, etc.). Rejected — explicitly out of scope per the do-not-rules; the Dockerfile packages the backend only, and the frontend continues to run via python -m http.server.

4. Trade-offs
Single-file main.py with thin supporting modules is easy to read end-to-end and matches the app's actual size, but it will not scale gracefully if the number of routes or business rules grows much further — there's no router registration pattern, no dependency-injection layer, and no service boundary to grow into.
In-memory storage keeps tests fast and deterministic (storage._reset() around every test) and removes an entire class of infrastructure concerns, but it means the app has zero durability — a container restart or process crash silently discards all data, which is a real limitation being carried forward on purpose, not by accident.
The Docker image is backend-only, so there is no single command that stands up the whole app; the frontend still needs python -m http.server run separately, which is a bit of a broken story for anyone trying to "just run the app" without already knowing the two-terminal convention from the README.
CI only runs pytest, not the Docker build — so a change that breaks the Dockerfile (e.g., a bad COPY path) would pass CI and only be caught locally, which is a gap between what's automated and what's actually shipped.
CORS is wide open (allow_origins=["*"]), which is fine for local dev against the Dockerized backend but is explicitly called out as not a production-safe setting.

I would do this differently by including memory that holds the earlier completed tasks even after i close the website or the file, i would add a productivity gauge to see how productive i am being with my tasks, and i would integrate login via a company to see how much are others being productive: what tasks are they on, what is in progress and what's urgent, who's the hardest worker and which department is slacking the most.

5. Consequences
Any future move to persistence (a database) or to multi-user/networked use (auth) requires an explicit, separate decision — the current architecture does not lay groundwork for either, by design.
Test suite behavior (72 passing tests, _reset() fixture) depends on storage staying in-memory and single-process; introducing a database or running multiple worker processes would break the existing test isolation strategy and require rework.
The Dockerfile and CI workflow are now committed, approved artifacts (Dockerfile/.dockerignore at commit 462e7a8, ci.yml at commit 36b84a9) and are treated as an on-the-record exception to the project's do-not-rules — any further Docker/CI/deployment change should still be confirmed first, since the exception covers what already exists, not open-ended expansion.
README.md §6 already documents the "no volume mount, data lost on stop" behavior of the container, so this is a known, communicated limitation rather than a silent gap.
[VERIFY] The CI workflow does not build or run the Docker image — this means Docker-specific breakage (e.g., a stale COPY path, a missing runtime dependency) is not caught automatically and relies on a human running docker build/docker run locally, per the README's own [VERIFY] note.
This note will be saved as docs/technical-note.md and should be added as a new row in README.md §11's documentation table, so it's discoverable alongside the other decision records under docs/midcourse/.

6. Open Questions
Should CI eventually also run docker build (and maybe a smoke-test docker run + /health check) so Docker breakage is caught automatically, or is that expansion out of scope for this course module?
Is there any appetite for a docker-compose setup that runs frontend + backend together, or does the two-terminal (uvicorn + python -m http.server) workflow stay the documented approach indefinitely?
[VERIFY] The requirements.txt httpx2 pin — is this actually a typo, and if so, should it be fixed now or left as-is until it causes a real problem?
At what point (if ever) does in-memory storage become a blocker for the course's grading/demo needs, and who decides that threshold?
Does the CORS allow_origins=["*"] setting need tightening even for local-only use, or is it accepted as-is for the remainder of the course?
