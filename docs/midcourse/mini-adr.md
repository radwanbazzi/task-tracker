# Mini-ADR: Due Dates, Overdue Filtering, and Task Comments

**Status:** Accepted  
**Project:** Task Tracker learning project  
**Scope:** Due dates, overdue filtering, task comments, and derived response fields

## Context

The existing Task Tracker backend uses Python, FastAPI, Pydantic v2, and an in-memory storage module.

The current implementation has:

- No database
- No ORM
- No database session
- No `APIRouter` or `include_router`
- No persistence between application restarts
- No SQLAlchemy or SQLModel dependency
- No test database

Task endpoints are defined directly in `main.py` using decorators such as `@app.get`, `@app.post`, `@app.patch`, and `@app.delete`.

Tests reset application state using `storage._reset()`.

This mini-ADR covers only:

- Optional task due dates
- Backend-computed overdue status
- An overdue task filter
- Task comments
- Derived `is_overdue` and `comment_count` response fields

It does not change the existing storage or endpoint organization.

## Decision

For the due-date, overdue-filtering, and task-comment features, the application will use **Option A — Minimum Architectural Change**.

The existing FastAPI application and in-memory storage module will be extended rather than replaced.

The implementation will add:

- Comment endpoints to `main.py` alongside the existing task endpoints
- Comment request and response schemas
- An in-memory comment collection in the existing storage layer
- An optional `due_date` field on stored tasks
- Small shared helper functions for derived task response values
- Synchronous comment cleanup when a task is deleted

Task and comment endpoints will continue calling the existing in-memory storage functions directly.

No router layer, service layer, repository layer, ORM, database session, migration system, or database will be introduced.

Overdue filtering will be performed in Python against the in-memory task collection. The overdue filter will combine with the existing status and priority filters using AND logic.

## Storage Approach

Tasks and comments will remain in application memory.

The storage module will be responsible for:

- Creating, reading, updating, and deleting tasks
- Creating, listing, and deleting comments
- Assigning task and comment identifiers
- Associating each comment with a `task_id`
- Returning only comments belonging to the requested task
- Returning comments in oldest-first order
- Removing all comments belonging to a task when that task is deleted
- Resetting both task and comment state through `storage._reset()` during tests

Comment cleanup will happen synchronously inside the task-deletion storage operation.

Because there is no database transaction, the storage function will remove the task and its related comments as one coordinated application-level operation before reporting success.

## Derived Response Fields Decision

### `is_overdue`

`is_overdue` will be a derived response field.

It will:

- Be included in task responses
- Not be accepted in task create or update requests
- Not be stored as authoritative task state
- Be recalculated whenever a task response is created

The rule is:

```text
is_overdue =
    due_date is not null
    AND due_date is strictly before today
    AND status is not Done
```

Therefore:

- A task due today is not overdue.
- A task without a due date is not overdue.
- A task with status `Done` is never overdue.
- Changing the due date or task status immediately changes the derived result.
- The value cannot become stale in storage.

Date access will be explicit and testable.

The helper will use this interface:

```python
compute_is_overdue(due_date, status, today)
```

`compute_is_overdue()` will take `today` as an explicit parameter and will never read the system clock internally.

Production callers will pass:

```python
date.today()
```

Tests will pass a controlled date directly, avoiding tests that depend on the real system date.

The same helper will be used for individual-task responses, task-list responses, and overdue filtering.

### `comment_count`

`comment_count` will also be a derived response field.

It will:

- Be included in task responses
- Not be accepted in create or update requests
- Not be stored on the task
- Be calculated from the authoritative in-memory comment collection

For each task, `comment_count` will equal the number of stored comments whose `task_id` matches that task.

This avoids maintaining a stored counter after:

- Comment creation
- Comment deletion
- Task deletion
- Test-state resets

The same response-building helper will be used by the task-list and individual-task endpoints so both return consistent `is_overdue` and `comment_count` values.

## Validation Approach

Pydantic v2 request schemas will continue handling input validation.

### Due-Date Validation

The due-date input logic will:

- Accept a valid ISO calendar date
- Accept `null`
- Normalize an empty string to `null`
- Reject invalid date formats
- Reject invalid calendar dates
- Reject natural-language dates
- Reject client-supplied derived fields
- Reject Boolean and integer inputs explicitly

The due-date validator must check the raw input before Pydantic performs date coercion.

Values such as the following must return HTTP 422:

```python
False
True
0
1
```

This explicit rejection is required because Pydantic v2 lax validation may otherwise interpret numeric values as Unix timestamps and coerce them into dates.

Empty-string normalization is a new rule introduced by the due-date feature. It is not based on existing assignee behavior.

For PATCH requests:

- `due_date: null` clears the due date.
- `due_date: ""` is normalized to `null` and clears the due date.
- Omitting the `due_date` field leaves the stored value unchanged.

### Comment Validation

The comment-create schema will:

- Require `text`
- Trim leading and trailing whitespace
- Reject blank or whitespace-only text
- Limit text to 1,000 characters
- Treat `author` as optional
- Trim leading and trailing whitespace from `author`
- Convert a missing, null, empty, or whitespace-only author to `null`
- Limit a non-null author to 50 characters
- Reject unexpected fields

## API Changes

The existing task endpoints in `main.py` will be updated to support due dates, derived fields, and overdue filtering.

The following comment endpoints will also be added directly to `main.py`:

```http
POST /tasks/{task_id}/comments
GET /tasks/{task_id}/comments
DELETE /tasks/{task_id}/comments/{comment_id}
```

After these additions, keeping all nine endpoints in `main.py` is acceptable for the current learning-project size.

Introducing `APIRouter` solely for these features would create a new organizational pattern without providing enough current benefit.

## Rationale

### Simplicity

This decision preserves the architecture that is already implemented.

The request flow remains:

```text
FastAPI endpoint in main.py
→ Pydantic validation
→ in-memory storage function
→ derived response helper
```

The implementation does not add:

- Routers
- Services
- Repositories
- An ORM
- Database sessions
- Migrations
- External infrastructure

Keeping all current and new endpoints in `main.py` is simpler and more consistent than introducing routing abstractions for a nine-endpoint learning application.

### Testability

The existing test pattern will continue using `storage._reset()` to isolate tests.

The in-memory architecture supports direct testing of:

- Valid due dates
- Missing and cleared due dates
- Empty-string normalization
- Invalid date formats
- Invalid calendar dates
- Explicit Boolean and integer rejection
- Date-dependent overdue rules
- Tasks due today
- Done tasks
- Combined overdue, status, and priority filters
- Comment text and author normalization
- Comment isolation between tasks
- Oldest-first comment ordering
- Comment deletion
- Derived comment-count updates
- Comment cleanup after deleting a task
- HTTP 404, 422, and 204 behavior

Passing `today` explicitly into `compute_is_overdue()` prevents date tests from depending on the machine clock and makes boundary cases deterministic.

### Local Run Ability

The features add no new setup or external service.

The application will continue running with the existing backend and frontend commands.

There is:

- No database initialization
- No migration command
- No database server
- No Docker setup
- No background process
- No additional runtime dependency beyond the libraries required for the existing FastAPI application

### Familiarity

The selected design uses concepts already present in the codebase:

- FastAPI decorators in `main.py`
- Pydantic schemas and validators
- Plain Python functions
- In-memory lists or collections
- Explicit filtering
- Direct storage calls
- Small reusable helpers

These patterns are understandable for an intermediate Python developer and make AI-generated changes easier to inspect against the existing project structure.

## AI Assumptions Corrected or Rejected

- Rejected the assumption that the project uses SQLite, an ORM, database sessions, foreign keys, cascades, or database transactions. The implemented project uses resettable in-memory storage.
- Rejected the assumption that a dedicated comments router should be introduced. The existing application defines endpoints directly in `main.py`, and consistency is preferable at the current size.
- Corrected the assumption that empty-string due-date normalization matches existing assignee behavior. The current assignee model does not normalize `""` to `null`; due-date normalization is a new feature rule.
- Rejected reading `date.today()` inside the overdue helper because hidden clock access would make date-dependent tests harder to control.
- Rejected storing `is_overdue` because it is derived from the due date, status, and current date and could become stale.
- Rejected storing `comment_count` because it can be calculated from the authoritative comment collection and a stored counter could become inconsistent.
- Rejected introducing service or repository layers because the current endpoint count and business-rule complexity do not justify them.

## Risks if the Project Grew

- In-memory task and comment data is lost whenever the application restarts and cannot be shared reliably between multiple application processes.
- Filtering tasks and calculating comment counts by scanning in-memory collections may become inefficient if the number of tasks or comments grows substantially.

If these risks become relevant, the storage implementation could later be replaced with persistent database storage while preserving the API schemas, explicit overdue function, and derived-field rules.
