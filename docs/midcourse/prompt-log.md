# Prompt Log

AI-assisted coding log for the mid-course project (Due dates \+ overdue filter, Task comments).

Tool used: VS Code agent mode, operating directly on this repository.

**How I use this file:** the prompt text is written *before* I run it. After each run I fill in what the AI returned, what I accepted / edited / rejected, and the verification result. Entries stay in the order I actually ran them, including the ones that went wrong.

---

## Reusable guardrail preamble

Prepended to every implementation prompt in this project:

Repository context (do not re-derive it, and do not assume anything beyond it):

\- Backend: Python 3, FastAPI, Pydantic v2. Files: backend/app/main.py,

  models.py, storage.py, business\_rules.py.

\- Storage is IN-MEMORY only: storage.py holds a module-level dict

  \_tasks: Dict\[str, TaskResponse\]. There is NO database, NO ORM, NO SQLAlchemy,

  NO SQLModel, NO session, NO migrations. Do not add any.

\- Endpoints live directly in main.py using @app decorators. There is no

  APIRouter. Do not introduce one.

\- All request models use model\_config \= ConfigDict(extra="forbid").

\- Status transitions are restricted in business\_rules.py to

  ToDo-\>InProgress, InProgress-\>Done, Done-\>InProgress. Nothing else.

\- Tests: pytest \+ Starlette TestClient, in backend/tests/. conftest.py resets

  state with storage.\_reset(). 19 tests currently pass.

Working rules:

\- Change ONLY the file(s) I name. Do not reformat, re-indent, reorder imports,

  or "tidy" anything you were not asked to change.

\- Do not add new third-party dependencies.

\- Do not modify backend/tests/ unless I explicitly say so.

\- Show me a diff of only the changed sections, then stop and wait for my

  approval before writing to disk.

---

# Feature A — Due dates \+ overdue filter

## A-P1 — Extend the Pydantic models

**Goal:** `due_date` accepted on create/update, returned on read; `is_overdue` present on the response model with a safe default.

**Prompt:**

\[guardrail preamble\]

Task: edit backend/app/models.py ONLY.

1\. Add an optional due\_date field to TaskCreate and to TaskUpdate, typed as

   Optional\[date\] using \`from datetime import date\`. Default None on both.

2\. Add to TaskResponse:

   \- due\_date: Optional\[date\]

   \- is\_overdue: bool \= False

   The default on is\_overdue matters: storage.py constructs TaskResponse

   objects directly, and those calls must keep working unchanged. The real

   value is computed later at response-build time, not here.

3\. Add a field\_validator on due\_date with mode="before", applied to both

   TaskCreate and TaskUpdate, that:

   \- converts an empty string or a whitespace-only string to None

   \- explicitly rejects bool and int values by raising ValueError, because

     Pydantic v2 lax mode would otherwise coerce 0 or False into a date via

     Unix epoch. \`isinstance(v, bool)\` must be checked BEFORE \`isinstance(v, int)\`,

     since bool is a subclass of int.

   \- passes every other value through untouched so Pydantic still handles

     normal parsing and still returns 422 for "21-07-2026" and "2026-02-30".

Constraints:

\- Do not touch the existing title validators, TaskStatus, or TaskPriority.

\- Do not touch any file other than models.py.

Output: the diff for models.py only, then wait for my approval.

**What the AI returned:** *(fill in)*

**Accepted / edited / rejected:** *(fill in)*

**Verification:** `pytest -v` → *(expect 19 passed)*

---

## A-P2 — Persist due\_date in the storage layer

**Goal:** `due_date` survives create, update, and explicit clearing.

**Prompt:**

\[guardrail preamble\]

Task: edit backend/app/storage.py ONLY.

1\. In add\_task(), pass payload.due\_date through to the TaskResponse being

   constructed.

2\. In update\_task(), the editable-field whitelist is currently

   {"title", "description", "status", "priority", "assignee"}.

   Add "due\_date" to it. Without this, due-date updates are silently dropped.

3\. Confirm that clearing works: update\_task uses

   payload.model\_dump(exclude\_unset=True), so a PATCH body that explicitly

   sends due\_date=null includes the key with value None and clears the field,

   while a PATCH body that omits due\_date leaves the stored value unchanged.

   Do not add special-case code for this — just tell me in your answer whether

   the existing logic already produces that behaviour, and only change code if

   it does not.

Constraints:

\- Do not change any function signature.

\- Do not touch get\_task\_by\_id, delete\_task, or \_reset.

\- Do not touch any file other than storage.py.

Output: the diff for storage.py only, then wait for my approval.

**What the AI returned:** *(fill in)*

**Accepted / edited / rejected:** *(fill in)*

**Verification:** `pytest -v` → *(expect 19 passed)*

---

## A-P3 — New shared rules helper (the testability decision)

**Goal:** overdue logic as a pure, date-injectable function. This is the step that keeps the date tests from breaking on a future calendar day.

**Prompt:**

\[guardrail preamble\]

Task: create ONE new file, backend/app/task\_rules.py. Do not modify any

existing file in this step.

The file contains exactly two functions:

1\. compute\_is\_overdue(due\_date: date | None, status: TaskStatus, today: date) \-\> bool

   Returns True only when ALL of these hold:

   \- due\_date is not None

   \- due\_date is STRICTLY earlier than today (a task due today is NOT overdue)

   \- status is not TaskStatus.DONE

   This function must NEVER call date.today() or datetime.now() internally.

   \`today\` is always passed in by the caller. This is a deliberate design

   decision so tests can pass a controlled date.

2\. build\_task\_response(task: TaskResponse, today: date) \-\> TaskResponse

   Returns a copy of the task (use model\_copy) with is\_overdue set to the

   result of compute\_is\_overdue. Does not mutate the input object, because the

   input is the object held in the in-memory store.

Constraints:

\- Import only from app.models and the standard library. Do NOT import from

  main.py or storage.py — that would create a circular import.

\- No I/O, no globals, no side effects.

Output: the full contents of the new file, then wait for my approval.

**What the AI returned:** *(fill in)*

**Accepted / edited / rejected:** *(fill in)*

**Verification:** `pytest -v` → *(expect 19 passed — the new file is not wired in yet, so this confirms I broke nothing)*

---

## A-P4 — Wire the helper in and add the overdue filter

**Goal:** every task-returning endpoint reports a live `is_overdue`, and `GET /tasks?overdue=true` filters correctly.

**Prompt:**

\[guardrail preamble\]

Task: edit backend/app/main.py ONLY.

1\. Import date from datetime and build\_task\_response from app.task\_rules.

2\. Every endpoint that returns a task or a list of tasks (list\_tasks,

   create\_task, get\_task, update\_task) must return its result through

   build\_task\_response, passing today=date.today(). Compute today ONCE per

   request, not once per task in a loop.

3\. Add an \`overdue: bool | None \= None\` query parameter to list\_tasks.

   \- When it is None, behaviour is unchanged.

   \- When True, return only tasks whose computed is\_overdue is True.

   \- When False, return only tasks whose computed is\_overdue is False.

   \- It combines with the existing status and priority filters using AND.

   \- Apply status and priority first via the existing

     storage.get\_all\_tasks(status=..., priority=...) call, then filter the

     result on overdue in Python. Do not reimplement the status or priority

     filtering.

   \- A combination that matches nothing returns 200 with \[\].

   \- FastAPI's bool parsing already returns 422 for ?overdue=notabool.

     Do not write custom parsing for that.

Constraints:

\- Do not change the /health endpoint.

\- Do not change delete\_task.

\- Do not change the validate\_status\_transition call or its position.

\- Do not change any existing 404 or 422 behaviour.

\- Do not touch any file other than main.py.

Output: the diff for main.py only, then wait for my approval.

**What the AI returned:** *(fill in)*

**Accepted / edited / rejected:** *(fill in)*

**Verification:** `pytest -v` → *(expect 19 passed)*, plus the manual curl checks recorded in verification.md.

---

## A-P5 — Weak prompt, rewritten

**The weak version I started with:**

add due dates to my task tracker

**Why it was weak:** no file named, no type or format specified, no statement that storage is in-memory, no rule for what "overdue" means, no boundary behaviour for a task due today, nothing about the restricted status transitions, and no instruction to show a diff before writing. Run as-is, an agent is free to invent a database, store `is_overdue` as a column, use `datetime` instead of `date`, and rewrite files I never asked it to touch.

**The strong rewrite:** prompts A-P1 through A-P4 above — the same work split into four reviewable steps, each naming exactly one file, each stating its constraints and its non-goals, each ending with "show me a diff and wait."

**What changed as a result:** *(fill in — what the weak prompt actually produced when you tried it, versus the split version)*

---

# Feature B — Task comments

*(To be filled in during Step 6, following the same pattern: models → storage → endpoints → tests, one file per prompt.)*

## B-P1 — *(title)*

**Prompt:**

**What the AI returned:** *(fill in)*

**Accepted / edited / rejected:** *(fill in)*

**Verification:** *(fill in)*

---

