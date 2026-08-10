# Mid-Course Project — Submission

**Student:** Youssef Bazzi **Course:** AI-Assisted Coding (AUB) **Project:** Task Tracker — two scoped features added to the Modules 1–3 build

---

## Repository

**URL:** [https://github.com/radwanbazzi/task-tracker](https://github.com/radwanbazzi/task-tracker)

**Branch to review:** `mid-course-project`

**Direct link to the submitted branch:** [https://github.com/radwanbazzi/task-tracker/tree/mid-course-project](https://github.com/radwanbazzi/task-tracker/tree/mid-course-project)

The repository is public.

---

## Features implemented

1. **Due dates \+ overdue filter** — optional `due_date` on every task, a backend-computed `is_overdue` flag, an "Overdue" pill on the task card, and a "Show overdue only" filter that combines with the existing status and priority filters using AND logic.  
     
2. **Task comments** — add, list, and delete comments on a task, with a comment count shown on the card and a comments panel inside the edit modal. Deleting a task also deletes its comments.

Both features are visible and usable in the frontend.

---

## Documentation

| Document | Link |
| :---- | :---- |
| User stories | [https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/user-stories.md](https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/user-stories.md) |
| Mini-ADR | [https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/mini-adr.md](https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/mini-adr.md) |
| Prompt log | [https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/prompt-log.md](https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/prompt-log.md) |
| Verification | [https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/verification.md](https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/verification.md) |
| Reflection | [https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/reflection.md](https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/docs/midcourse/reflection.md) |
| README | [https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/README.md](https://github.com/radwanbazzi/task-tracker/blob/mid-course-project/README.md) |

---

## Tests

| File | Tests | Covers |
| :---- | ----: | :---- |
| `backend/tests/test_tasks.py` | 19 | Modules 1–3, unchanged |
| `backend/tests/test_due_dates.py` | 26 | Feature A |
| `backend/tests/test_comments.py` | 27 | Feature B |
| **Total** | **72** | 53 new tests added |

---

## How to run

Full instructions are in the README. In short:

\# Backend

cd backend

python \-m venv venv

.\\venv\\Scripts\\activate

pip install \-r ..\\requirements.txt

uvicorn app.main:app \--reload

\# API docs at http://127.0.0.1:8000/docs

\# Frontend (second terminal)

cd frontend

python \-m http.server 5500

\# UI at http://127.0.0.1:5500

\# Tests

cd backend

.\\venv\\Scripts\\activate

pytest \-v

Storage is in memory — there is no database, and data does not survive a backend restart. This is intentional for the scope of this project.  
