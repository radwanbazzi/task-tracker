# Prompt Log

AI-assisted coding log for the mid-course project (Feature A: due dates \+ overdue filter, Feature B: task comments).

Tool used: VS Code agent mode, operating directly on this repository.

**How I use this file:** the prompt text is written *before* I run it. After each run I record what the AI returned, what I accepted / edited / rejected, and the verification result. Entries stay in the order I actually ran them, including the ones that went wrong.

---

## Reusable guardrail preamble

Prepended to every implementation prompt in this project:

Repository context (do not re-derive it, and do not assume anything beyond it):

\- Backend: Python 3, FastAPI, Pydantic v2. Files: backend/app/main.py,

  models.py, storage.py, business\_rules.py, task\_rules.py.

\- Storage is IN-MEMORY only: storage.py holds a module-level dict

  \_tasks: Dict\[str, TaskResponse\]. There is NO database, NO ORM, NO SQLAlchemy,

  NO SQLModel, NO session, NO migrations. Do not add any.

\- Endpoints live directly in main.py using @app decorators. There is no

  APIRouter. Do not introduce one.

\- All request models use model\_config \= ConfigDict(extra="forbid").

\- Status transitions are restricted in business\_rules.py to

  ToDo-\>InProgress, InProgress-\>Done, Done-\>InProgress. Nothing else.

\- Tests: pytest \+ Starlette TestClient, in backend/tests/. conftest.py resets

  state with storage.\_reset().

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

**Goal:** `due_date` accepted on create/update and returned on read; `is_overdue` present on the response model with a safe default.

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

**What the AI returned:** all three changes as specified. `due_date: Optional[date] = None` added to `TaskCreate` and `TaskUpdate`; `due_date: Optional[date] = None` and `is_overdue: bool = False` added to `TaskResponse`; and a `_normalize_due_date` classmethod validator with `mode="before"` on both request models. The bool check is correctly placed before the int check. The import line was widened to `from datetime import date, datetime` rather than adding a second import.

Notable: the validator body is **duplicated verbatim** across `TaskCreate` and `TaskUpdate` rather than extracted to a shared helper. Logged as a refactor candidate rather than fixed here, to keep this step's diff to one concern.

**Verification:** `pytest -v` → 19 passed.

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

**What the AI returned:** a two-line diff — `due_date=payload.due_date` added to the `TaskResponse(...)` construction in `add_task()`, and `"due_date"` appended to the whitelist set in `update_task()`. On point 3 it confirmed that the existing `exclude_unset=True` logic already distinguishes "omitted" from "explicitly null" and correctly declined to add code.

This was the highest-risk step for a silent bug: without the whitelist change the API would have returned 200 on a due-date PATCH while quietly discarding the value, which no status-code assertion would have caught.

**Verification:** `pytest -v` → 19 passed.

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

**What the AI returned:** a 15-line file with exactly the two functions requested. `compute_is_overdue` is a single boolean expression — `due_date is not None and due_date < today and status is not TaskStatus.DONE` — with no clock access anywhere in the file. `build_task_response` uses `task.model_copy(update={...})`, so the object held in the in-memory store is never mutated. Imports are limited to `datetime.date` and `app.models`, so no circular import risk.

This is the decision the whole test strategy rests on: because `today` is a parameter, the tests can construct dates relative to `date.today()` and will still pass on any future calendar day, with no clock-mocking library.

**Verification:** `pytest -v` → 19 passed. The count is unchanged on purpose — this step added a file that nothing imports yet, so a green run proves only that I broke nothing.

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

**What the AI returned:** `today = date.today()` computed once at the top of each of the four task-returning endpoints, with `build_task_response(task, today=today)` applied to each result. `list_tasks` gained `overdue: bool | None = None`, builds the response list first, then filters it — reusing the existing `storage.get_all_tasks(status=..., priority=...)` call rather than reimplementing the status/priority filters, which is what makes the AND-combining behaviour fall out for free. No custom bool parsing was added, so `?overdue=notabool` returns 422 from FastAPI's own validation. `/health`, `delete_task`, and the `validate_status_transition` call were left untouched.

Minor style note for later review: the filter uses `task.is_overdue is overdue` (identity comparison). This works because Python's `True`/`False` are singletons, but `==` would be more idiomatic and less fragile.

**Verification:** `pytest -v` → 19 passed, plus the 14 manual `/docs` checks recorded in verification.md.

---

## A-P5 — Feature A frontend

**Goal:** due date visible and editable in the UI; overdue tasks visually flagged; an overdue filter that goes through the backend.

Two assumptions in my user stories did not survive contact with the code, and I corrected them before writing this prompt:

1. Story A4 said the overdue control would sit "alongside the existing status/priority filters." **There are no such controls.** The three Kanban columns *are* the status view. Replaced with a single "Show overdue only" checkbox in the page header.  
2. My original plan filtered the task array in JavaScript. That would have left the `?overdue=true` endpoint I had just built completely unexercised by the UI, so the filter had to be pushed into `fetchTasks()` as a query parameter.

**Prompt:**

\[guardrail preamble\]

Task: edit frontend/index.html ONLY. This is Feature A's frontend layer.

The backend is already finished and tested — every task object returned by

the API now includes \`due\_date\` (an ISO "YYYY-MM-DD" string, or null) and

\`is\_overdue\` (a boolean computed by the backend).

Make exactly these changes and nothing else.

\--- HTML \---

1\. In the modal form, add ONE new form-field block immediately after the

   existing Assignee block (the div containing \#taskAssignee):

     \<div class="form-field"\>

       \<label for="taskDueDate"\>Due date\</label\>

       \<input id="taskDueDate" name="due\_date" type="date" /\>

     \</div\>

   Use type="date". Do not add a "required" attribute.

2\. In the page header, immediately after the \#newTaskBtn button, add a

   checkbox with id="overdueFilter" and a visible label "Show overdue only".

\--- JavaScript \---

3\. formValues(): add \`due\_date\`, read from \#taskDueDate. An empty input must

   be sent as null, matching how \`assignee\` is handled (\`value || null\`).

4\. openEditModal(task): populate \#taskDueDate with \`task.due\_date || ''\`.

   Assign the RAW ISO string exactly as the API returned it. Do NOT reformat,

   parse, or localise it. handleTaskFormSubmit diffs form values against

   editingTask by string comparison, so any reformatting would make an

   unchanged date look changed on every save.

5\. openCreateModal(): this already calls form.reset(), which clears a date

   input automatically. Check whether an explicit clear is needed. If not,

   say so and change nothing here.

6\. fetchTasks(): accept an \`overdueOnly\` boolean argument (default false).

   When true, request \`${BACKEND\_URL}/tasks?overdue=true\`. The filtering MUST

   happen on the backend. Do not filter the array in JavaScript.

7\. loadAndRender(): read \#overdueFilter's checked state, pass it to fetchTasks().

8\. In DOMContentLoaded, add a 'change' listener on \#overdueFilter calling

   loadAndRender(). Do not restructure that block.

9\. renderBoard(), card template only: inside .task-meta add a

   \<span class="due-date"\> rendered ONLY when task.due\_date is truthy, and a

   \<span class="overdue-pill"\>Overdue\</span\> rendered ONLY when task.is\_overdue

   is true. Read task.is\_overdue directly. Do NOT compare dates in JavaScript.

   Keep using escapeHtml() for interpolated task data.

\--- CSS \---

10\. Add .overdue-pill and .due-date rules to the existing \<style\> block,

    matching the visual language of .priority and .assignee. The pill must be

    clearly visible.

Do NOT modify: handleTaskFormSubmit, patchTaskStatus, getResponseMessage, any

drag-and-drop handler, closeTaskModal, setState, showErrorMessage,

clearErrorMessage, showTaskFormError, clearTaskFormError, escapeHtml, the

empty-state placeholder logic, the column count logic, the existing sort

comparator in renderBoard, BACKEND\_URL, PRIORITY\_ORDER, STATUSES.

Do not reformat, re-indent, or reorder any part of the file you were not asked

to change. This file is 870 lines and I will be checking the diff size.

Output: a diff showing only the changed HTML blocks, the changed JS functions,

and the added CSS rules. Then stop and wait for my approval.

**What the AI returned:** all ten changes, correctly scoped. The card template gained two conditional spans using ternaries that render nothing when the value is absent. `.due-date` reuses the existing `var(--muted)` colour and `.overdue-pill` matches the `.priority` pill shape with a red palette. The raw ISO string is assigned straight into the date input, so the `handleTaskFormSubmit` diff logic still correctly skips `due_date` when it hasn't changed.

**Verification:** browser checks recorded in verification.md, including the DevTools Network capture proving the request URL is `/tasks?overdue=true` — i.e. the filter is genuinely server-side.

---

## A-P6 — Weak prompt, rewritten

**The weak version I started with:**

add due dates to my task tracker

**Why it was weak:** no file named, no type or format specified, no statement that storage is in-memory, no rule for what "overdue" means, no boundary behaviour for a task due today, nothing about the restricted status transitions, and no instruction to show a diff before writing. Run as-is, an agent is free to invent a database, store `is_overdue` as a persisted column, use `datetime` instead of `date`, and rewrite files I never asked it to touch.

**The strong rewrite:** prompts A-P1 through A-P5 — the same work split into five reviewable steps, each naming exactly one file, each stating its constraints and its non-goals, each ending with "show me a diff and wait."

---

# Feature B — Task comments

Design decisions carried in from the mini-ADR, so the agent doesn't get to re-litigate them:

- Comment schemas go in the existing `models.py`, not a new file. The ADR commits to extending the current structure rather than adding patterns.  
- `comment_count` is a **derived** response field, never stored on the task.  
- `task_rules.py` must stay free of storage imports, so `comment_count` is passed into `build_task_response` as an argument rather than looked up inside it.

## B-P1 — Comment schemas and the derived count field

**Prompt:**

\[guardrail preamble\]

Task: edit backend/app/models.py ONLY.

1\. Add a CommentCreate request model with model\_config \= ConfigDict(extra="forbid"):

   \- text: str

   \- author: Optional\[str\] \= None

   Validators:

   \- text: strip whitespace. If the result is empty, raise

     ValueError("Comment text is required and cannot be blank").

     If the stripped result exceeds 1000 characters, raise a ValueError.

     Trim FIRST, then measure length.

   \- author: mode="before". Strip whitespace. Convert None, empty string, or a

     whitespace-only string to None. If the stripped result exceeds 50

     characters, raise a ValueError. A blank author is never an error — only

     blank text is.

2\. Add a CommentResponse model with model\_config \= ConfigDict(extra="forbid"):

   \- id: str

   \- task\_id: str

   \- text: str

   \- author: Optional\[str\]

   \- created\_at: datetime

3\. Add to TaskResponse: comment\_count: int \= 0

   The default matters for the same reason is\_overdue's did — storage.py

   constructs TaskResponse objects directly and those calls must keep working.

   The real value is computed at response-build time.

Constraints:

\- Do not modify TaskCreate, TaskUpdate, TaskStatus, TaskPriority, or any

  existing validator.

\- Do not add comment\_count or is\_overdue to any request model. They are

  response-only, and extra="forbid" must keep rejecting them on input.

\- Do not touch any file other than models.py.

Output: the diff for models.py only, then wait for my approval.

**Verification:** `pytest -v` → *(expect 45 passed — Feature A's suite must stay green; nothing consumes these models yet)*

---

## B-P2 — Comment storage and cascade delete

**Prompt:**

\[guardrail preamble\]

Task: edit backend/app/storage.py ONLY.

1\. Add a module-level dict alongside the existing \_tasks:

   \_comments: Dict\[str, CommentResponse\] \= {}

2\. Add these functions:

   \- add\_comment(task\_id: str, payload: CommentCreate) \-\> CommentResponse

     Generates an id with uuid4().hex and created\_at with

     datetime.now(timezone.utc), exactly matching how add\_task does it.

   \- get\_comments\_for\_task(task\_id: str) \-\> List\[CommentResponse\]

     Returns only comments whose task\_id matches.

     ORDERING: iterate \_comments.values() in natural dict order and filter.

     Python dicts preserve insertion order, so this is already oldest-first and

     fully deterministic. Do NOT sort by created\_at — two comments created in

     the same millisecond could tie, and the ids are random uuid hex so they

     provide no usable tiebreak.

   \- delete\_comment(task\_id: str, comment\_id: str) \-\> bool

     Returns True only if the comment exists AND belongs to that task\_id.

     Returns False otherwise. Do not raise HTTPException here — storage does

     not know about HTTP.

   \- count\_comments\_for\_task(task\_id: str) \-\> int

3\. Modify delete\_task(task\_id) so that when it deletes a task it ALSO removes

   every comment whose task\_id matches, in the same call, before returning

   True. Do not change its signature or its return type.

4\. Modify \_reset() to clear \_comments as well as \_tasks. Without this, comment

   state leaks between tests and you get failures that depend on test order.

Constraints:

\- Do not change any existing task function's signature or behaviour.

\- Do not import from main.py or task\_rules.py.

\- Do not touch any file other than storage.py.

Output: the diff for storage.py only, then wait for my approval.

**Verification:** `pytest -v` → *(expect 45 passed)*

---

## B-P3 — Thread comment\_count through the response helper

**Prompt:**

\[guardrail preamble\]

Task: edit backend/app/task\_rules.py ONLY.

Change build\_task\_response so its signature is:

    build\_task\_response(task: TaskResponse, today: date, comment\_count: int \= 0\) \-\> TaskResponse

and include comment\_count in the model\_copy update dict alongside is\_overdue.

Do NOT import storage into this module and do NOT look the count up inside the

function. The count is passed in by the caller. This module must stay pure and

free of storage dependencies — that is what keeps it unit-testable and free of

circular imports.

Leave compute\_is\_overdue completely unchanged.

The default of 0 keeps every existing call site working without modification,

so this step must not break anything.

Constraints:

\- Do not touch any file other than task\_rules.py.

Output: the diff, then wait for my approval.

**Verification:** `pytest -v` → *(expect 45 passed — the default argument means existing callers are unaffected)*

---

## B-P4 — Comment endpoints and count wiring

**Prompt:**

\[guardrail preamble\]

Task: edit backend/app/main.py ONLY.

1\. Add three endpoints, placed AFTER the existing task endpoints:

   POST /tasks/{task\_id}/comments

     \- response\_model=CommentResponse, status\_code=201

     \- 404 with detail "Task not found" if the task does not exist.

       Check this BEFORE creating anything.

     \- Otherwise returns storage.add\_comment(task\_id, payload)

   GET /tasks/{task\_id}/comments

     \- response\_model=list\[CommentResponse\], status 200

     \- 404 with detail "Task not found" if the task does not exist

     \- A task that exists with no comments returns 200 and \[\]

       (an empty list is NOT a 404\)

   DELETE /tasks/{task\_id}/comments/{comment\_id}

     \- status\_code=204, returns None

     \- 404 if the task does not exist

     \- 404 if storage.delete\_comment returns False (comment missing, or it

       belongs to a different task)

2\. Update all four task-returning endpoints (list\_tasks, create\_task,

   get\_task, update\_task) to pass

   comment\_count=storage.count\_comments\_for\_task(\<task id\>)

   into build\_task\_response.

Constraints:

\- Do not use APIRouter. Use @app decorators like every other endpoint here.

\- Do not change /health, delete\_task, or any existing task behaviour.

\- Do not change the validate\_status\_transition call or its position.

\- Do not add authentication, pagination, or comment editing.

\- Do not touch any file other than main.py.

Output: the diff for main.py only, then wait for my approval.

**Verification:** `pytest -v` → *(expect 45 passed)*, plus manual `/docs` checks recorded in verification.md.

---

## B-P5 — Feature B pytest suite

**Prompt:**

You are a senior Python developer writing pytest tests for a FastAPI app.

Context files: @app/main.py @app/models.py @app/storage.py

@app/business\_rules.py @app/task\_rules.py @tests/conftest.py

Generate ONE file. Output only one code block, preceded by:

\# FILE: tests/test\_comments.py

This file covers Feature B (task comments) ONLY. tests/conftest.py,

tests/test\_tasks.py and tests/test\_due\_dates.py already exist and must NOT be

regenerated, renamed, or modified.

\============================================================

Existing fixtures available from conftest.py (reuse, do not redefine)

\============================================================

\- \_reset\_storage : autouse, calls storage.\_reset() before and after each test

\- client         : returns TestClient(app)

\- created\_task   : posts {"title": "fixture task"}, asserts 201, returns JSON

\============================================================

FILE \- tests/test\_comments.py

\============================================================

Generate these named tests:

POST /tasks/{task\_id}/comments:

\- test\_add\_comment\_returns\_201\_with\_full\_body

\- test\_add\_comment\_trims\_surrounding\_whitespace\_from\_text

\- test\_add\_comment\_without\_author\_stores\_null\_author

\- test\_add\_comment\_with\_whitespace\_only\_author\_stores\_null\_author

\- test\_add\_comment\_blank\_text\_returns\_422\_with\_exact\_detail\_message

\- test\_add\_comment\_whitespace\_only\_text\_returns\_422

\- test\_add\_comment\_text\_over\_1000\_chars\_returns\_422

\- test\_add\_comment\_author\_over\_50\_chars\_returns\_422

\- test\_add\_comment\_unknown\_field\_returns\_422

\- test\_add\_comment\_to\_missing\_task\_returns\_404

GET /tasks/{task\_id}/comments:

\- test\_list\_comments\_returns\_all\_comments\_for\_task

\- test\_list\_comments\_for\_task\_with\_none\_returns\_200\_empty\_list

\- test\_list\_comments\_excludes\_other\_tasks\_comments

\- test\_list\_comments\_returns\_oldest\_first

\- test\_list\_comments\_for\_missing\_task\_returns\_404

DELETE /tasks/{task\_id}/comments/{comment\_id}:

\- test\_delete\_comment\_returns\_204\_no\_body

\- test\_delete\_comment\_removes\_it\_from\_subsequent\_list

\- test\_delete\_missing\_comment\_returns\_404

\- test\_delete\_comment\_belonging\_to\_another\_task\_returns\_404

\- test\_delete\_comment\_on\_missing\_task\_returns\_404

comment\_count as a derived task field:

\- test\_task\_response\_includes\_comment\_count\_zero\_by\_default

\- test\_comment\_count\_increases\_after\_adding\_comment

\- test\_comment\_count\_decreases\_after\_deleting\_comment

\- test\_comment\_count\_present\_on\_list\_tasks\_endpoint

\- test\_client\_supplied\_comment\_count\_returns\_422

Cascade delete:

\- test\_deleting\_task\_removes\_its\_comments\_from\_storage

\- test\_deleting\_task\_does\_not\_remove\_other\_tasks\_comments

Hard constraints:

\- Use TestClient only. Do not use AsyncClient.

\- Do not mock storage. Use the real in-memory storage with the reset fixture.

\- For the cascade tests, the comments endpoint returns 404 once the parent task

  is gone, so you cannot verify cleanup through the API. Import

  \`from app import storage\` and inspect storage.\_comments directly.

\- The exact 422 detail message for blank text is

  "Comment text is required and cannot be blank". Assert on that string.

\- Do not call r.json() on a 204 response; assert r.content \== b"".

\- For ordering, create comments in a known sequence and assert the returned

  texts match that sequence exactly. Do not assert on timestamps.

\- Assert exact status codes and exact field values, not truthiness.

\- Do not skip, rename, merge, or omit any listed test.

\- Do not add tests unrelated to Feature B.

\- Use the exact route paths from main.py.

Output only the one file.

**Verification:** `pytest -v` → *(expect 45 \+ 27 \= 72 passed)*

---

## B-P6 — Feature B frontend

Run this only after B-P5 is green. Note the create-mode trap: a task being created has no id yet, so there is nothing to attach comments to.

**Prompt:**

\[guardrail preamble\]

Task: edit frontend/index.html ONLY. This is Feature B's frontend layer.

The backend is finished and tested. Every task object now includes

comment\_count (an integer). Comments live at:

  GET    /tasks/{task\_id}/comments   \-\> 200, list

  POST   /tasks/{task\_id}/comments   \-\> 201, {text, author?}

  DELETE /tasks/{task\_id}/comments/{comment\_id} \-\> 204

Make exactly these changes and nothing else.

\--- HTML \---

1\. Inside \#taskModal, AFTER the closing \</form\> tag of \#taskForm, add a

   section with id="commentsSection" containing:

   \- a heading "Comments"

   \- an empty \<div id="commentsList"\>\</div\>

   \- a small form with id="commentForm" holding

     \<input id="commentAuthor" type="text" placeholder="Your name (optional)"\>,

     \<textarea id="commentText" required\>\</textarea\>, and a submit button

   Keep it OUTSIDE \#taskForm. Nesting a form inside a form is invalid HTML and

   would break the existing task submit handler.

\--- JavaScript \---

2\. openCreateModal(): hide \#commentsSection. A task that does not exist yet has

   no id, so there is nothing to attach comments to.

3\. openEditModal(task): show \#commentsSection, clear \#commentText and

   \#commentAuthor, then load and render that task's comments.

4\. New function loadComments(taskId): GET the comments and render them into

   \#commentsList. Each rendered comment shows its text, its author, and its

   created\_at. When author is null, display "Anonymous" — never the literal

   string "null" and never a blank gap. Each comment gets a delete button.

   Use escapeHtml() on every interpolated value.

5\. New function handleAddComment(event): preventDefault, POST the comment. On

   success, reload the comment list and refresh the board so the card count

   updates. On failure, show the server's error message via the existing

   getResponseMessage() helper and leave the list and count exactly as they

   were.

6\. New function handleDeleteComment(taskId, commentId): DELETE, then reload the

   list and refresh the board. On failure leave the list and count unchanged.

7\. renderBoard(), card template only: inside .task-meta add a

   \<span class="comment-count"\> rendered ONLY when task.comment\_count \> 0\.

   Read the value from the API. Do NOT fetch comments per card.

8\. In DOMContentLoaded, register the submit listener for \#commentForm.

   Do not restructure that block.

\--- CSS \---

9\. Add rules for \#commentsSection, the comment list items, and .comment-count,

   matching the existing visual language.

Do NOT modify: handleTaskFormSubmit, formValues, patchTaskStatus,

getResponseMessage, escapeHtml, any drag-and-drop handler, closeTaskModal,

fetchTasks, the overdue filter logic, the empty-state placeholder logic, the

column count logic, BACKEND\_URL, PRIORITY\_ORDER, STATUSES.

Do not reformat, re-indent, or reorder anything you were not asked to change.

I will be checking the diff size.

Output: a diff showing only the changed HTML blocks, the new and changed JS

functions, and the added CSS rules. Then stop and wait for my approval.

**Verification:** *(browser checks — see verification.md)*

---

## B-P7 — Weak prompt, rewritten

**The weak version:**

add comments to tasks

**it was weak and non specific**

---

# Shared — focused refactor

Run **after** both feature suites are green and the Break Tests have proven the tests are trustworthy. Refactoring before the Break Test means changing code under a safety net that has not been validated.

**Refactor target:** `_normalize_due_date` is duplicated verbatim in `TaskCreate` and `TaskUpdate` (introduced in A-P1). Feature B adds the same shape of duplication for comment text and author trimming. Extracting these into shared validator helpers is a small, justifiable change with a clear before/after.

**Prompt:**

\[guardrail preamble\]

Task: refactor backend/app/models.py ONLY. This is a pure refactor — the

external behaviour of the API must not change at all.

Problem: the \_normalize\_due\_date validator body is duplicated verbatim in

TaskCreate and TaskUpdate. The comment validators added for Feature B have

similar duplication.

Extract the shared logic into module-level helper functions that each

field\_validator delegates to. Do not change:

\- any field name, type, or default

\- any error message text

\- any validation rule or its ordering

\- the extra="forbid" configuration on any model

Before you write anything, list the exact behaviours that must be identical

before and after, so I can check them against my test suite.

Output: first that behaviour list, then the diff. Then wait for my approval.

**Verification:** full suite green before AND after, with identical test counts. A refactor that changes a test result is not a refactor.

---

