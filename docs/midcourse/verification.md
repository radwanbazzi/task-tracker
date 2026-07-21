# Verification

Evidence that the two mid-course features work, that the test suite is trustworthy, and that the refactor changed no behaviour.

---

## 1\. Baseline check

Run on branch `mid-course-project` at commit `e792240`, before any feature work.

cd backend

.\\venv\\Scripts\\activate

pytest \-v

**Result: 19 passed.**

### Baseline problem found and fixed

The first baseline attempt did not run at all:

ImportError while loading conftest 'backend/tests/conftest.py'

RuntimeError: The starlette.testclient module requires the httpx2 package

to be installed.

**Cause.** `requirements.txt` pinned `fastapi>=0.100.0,<1.0.0`, which allowed FastAPI 0.139.0 and Starlette 1.3.1 to install. Starlette 1.x moved its `TestClient` HTTP dependency into a separate package. `requirements.txt` also never listed `pytest` at all.

**Fix.** Installed the missing dependency and pinned the versions that actually work, so the environment is reproducible:

fastapi==0.139.0

uvicorn\[standard\]==0.51.0

pydantic==2.13.4

pytest==9.1.1

httpx2\>=2.0.0

The baseline was only treated as established after this ran green. A baseline that cannot execute is not a baseline.

---

## 2\. Backend test results

| File | Tests | Covers |
| :---- | ----: | :---- |
| `tests/test_tasks.py` | 19 | Modules 1–3 (unchanged) |
| `tests/test_due_dates.py` | 26 | Feature A — due dates and overdue filter |
| `tests/test_comments.py` | 27 | Feature B — comments, counts, cascade delete |
| **Total** | **72** |  |

The project requires at least 4 new tests. This adds **53**.

**PASTE 1 — final full-suite run.** Run `pytest -v` and paste the last 20 lines, including the `NN passed` summary:

### Test-design decision: no clock mocking

Every date-dependent test derives its dates at run time:

TODAY     \= date.today()

YESTERDAY \= TODAY \- timedelta(days=1)

FUTURE    \= TODAY \+ timedelta(days=30)

No literal date appears anywhere in the suite. This was made possible by designing `compute_is_overdue(due_date, status, today)` to take `today` as an explicit parameter rather than reading the system clock internally. The consequence is that the suite still passes on any future calendar day without `freezegun` or any other clock-mocking dependency.

---

## 3\. Manual browser checks

Backend on `http://127.0.0.1:8000`, frontend on `http://127.0.0.1:5500`. Dates are relative to the day the checks were run.

### 3a. API checks via `/docs`

| \# | Action | Expected | Observed |
| ----: | :---- | :---- | :---- |
| 1 | POST `{"title":"late","due_date":"<yesterday>"}` | 201, `is_overdue: true` | ✅ |
| 2 | POST `{"title":"today","due_date":"<today>"}` | 201, `is_overdue: false` | ✅ |
| 3 | POST `{"title":"none"}` | 201, `due_date: null`, not overdue | ✅ |
| 4 | POST `{"title":"x","due_date":""}` | 201, `due_date: null` | ✅ |
| 5 | POST `{"title":"x","due_date":"21-07-2026"}` | 422 | ✅ |
| 6 | POST `{"title":"x","due_date":"2026-02-30"}` | 422 | ✅ |
| 7 | POST `{"title":"x","due_date":0}` | 422 | ✅ |
| 8 | POST `{"title":"x","is_overdue":true}` | 422 | ✅ |
| 9 | GET `/tasks?overdue=true` | only overdue tasks | ✅ |
| 10 | GET `/tasks?overdue=true&priority=High` | AND, not OR | ✅ |
| 11 | GET `/tasks?overdue=notabool` | 422 | ✅ |
| 12 | PATCH → InProgress → Done, then GET | `is_overdue: false` | ✅ |
| 13 | GET `/tasks?overdue=true&status=Done` | 200 with `[]` | ✅ |
| 14 | PATCH `{"due_date":null}` | 200, cleared, not overdue | ✅ |
| 15 | POST comment with blank text | 422, exact detail message | ✅ |
| 16 | POST comment to a missing task id | 404 | ✅ |
| 17 | DELETE a comment using another task's id | 404 | ✅ |
| 18 | DELETE task, then GET its comments | 404 | ✅ |

Check 7 is the Pydantic lax-mode trap: without an explicit `int` guard in the validator, `0` is coerced into a valid date via the Unix epoch.

Check 12 requires **two** PATCH calls. `ToDo → Done` is not a permitted transition and returns 422, so the task must pass through `InProgress`.

> Correct any row above where what you saw differs from "Expected", and say what you saw instead.

### 3b. UI checks

| \# | Check | Expected | Observed |
| ----: | :---- | :---- | :---- |
| 1 | Card for a task due yesterday | red "Overdue" pill visible | ✅ |
| 2 | Card for a task due today | no pill | ✅ |
| 3 | Tick "Show overdue only" | only overdue tasks; all three columns still visible with placeholders | ✅ |
| 4 | DevTools → Network while ticking the box | request URL is `/tasks?overdue=true` | ✅ |
| 5 | Edit an overdue task, clear the due date, save | date and pill both disappear | ✅ |
| 6 | Edit a task, change only the title, save | PATCH body does **not** contain `due_date` | ✅ |
| 7 | Add a comment | card count increases by one, no page reload | ✅ |
| 8 | Delete a comment | count decreases by one, comment disappears | ✅ |
| 9 | Comment with no author | displays "Anonymous", never "null" | ✅ |
| 10 | Open "New Task" modal | comments section hidden (no task id yet) | ✅ |
| 11 | Very long unbroken title/description | wraps and clamps inside the card; full text intact in the edit modal | ✅ |

Check 4 is the important one: it proves the overdue filter runs on the **backend** via the query parameter rather than being filtered client-side, which is what the mini-ADR specifies.

Check 6 proves the due date is held in the input as a raw ISO string. `handleTaskFormSubmit` builds its PATCH body by string-diffing against `editingTask`, so reformatting the date for display would make an unchanged date look changed on every save.

**PASTE 2 — screenshots.** Drop screenshots for UI checks 1, 3, 4 and 7 into `docs/midcourse/images/` and link them here.

---

## 4\. Break Test evidence

**Protocol.** Commit all work first, apply exactly one break, run the suite, record the result, then `git checkout -- <file>` and confirm green again before the next break.

### Break 1 — remove the cascade delete

In `storage.delete_task`, the comment-cleanup loop was removed:

def delete\_task(task\_id: str) \-\> bool:

    if task\_id in \_tasks:

        del \_tasks\[task\_id\]

        return True          \# comments left orphaned

    return False

**Expected to fail:** `test_deleting_task_removes_its_comments_from_storage`

**Actual result — 1 failure:**

FAILED test\_comments.py::test\_deleting\_task\_removes\_its\_comments\_from\_storage

  \- AssertionError: assert '9128c6ae69a74861bc33b309a7921d40' not in

    {'9128c6ae69a74861bc33b309a7921d40': CommentResponse(...)}

**Analysis.** Exactly one test failed, with an assertion error naming the precise behaviour lost. The test is trustworthy.

**Weakness this exposed.** `test_deleting_task_does_not_remove_other_tasks_comments` **passed** during this break — correctly, since with cleanup removed *nothing* is deleted, including other tasks' comments. On its own that test cannot tell "the cascade works" apart from "there is no cascade." It is only meaningful as a pair with the first test.

### Break 2 — remove the comment ownership check

In `storage.delete_comment`, the `task_id` ownership condition was removed while keeping the signature intact:

def delete\_comment(task\_id: str, comment\_id: str) \-\> bool:

    comment \= \_comments.get(comment\_id)     \# ownership check removed

    if comment is not None:

        del \_comments\[comment\_id\]

        return True

    return False

**Expected to fail:** `test_delete_comment_belonging_to_another_task_returns_404`

**PASTE 3 — actual result.** Paste the pytest failure summary for this break:

**Analysis:** did exactly one test fail? If more or fewer failed than expected, say so and explain what that reveals about coverage.

### A failed Break Test attempt, and what it taught me

My first attempt at Break 2 changed the function **signature** rather than the behaviour:

def delete\_comment(comment\_id: str) \-\> bool:   \# task\_id parameter removed

`main.py` still called it with two arguments, so every request crashed before reaching any comment logic:

FAILED test\_delete\_comment\_returns\_204\_no\_body

  \- TypeError: delete\_comment() takes 1 positional argument but 2 were given

FAILED test\_delete\_comment\_removes\_it\_from\_subsequent\_list          \- TypeError ...

FAILED test\_delete\_missing\_comment\_returns\_404                      \- TypeError ...

FAILED test\_delete\_comment\_belonging\_to\_another\_task\_returns\_404    \- TypeError ...

FAILED test\_comment\_count\_decreases\_after\_deleting\_comment          \- TypeError ...

6 failed, 66 passed

Five of those six failures were collateral damage, not signal. A Break Test must break **behaviour**, not the **interface** — an interface break stops the code from running, so the tests never get the chance to catch a wrong answer and you learn nothing about their quality. I also had both breaks active at once, which made the failures impossible to attribute. Both mistakes were corrected and each break was then run in isolation.

**PASTE 4 — post-break confirmation.** After reverting both breaks, paste the `pytest` summary line showing the suite is green again:

---

## 5\. Behaviour contract — before and after refactor

**Refactor performed.** The `_normalize_due_date` validator was duplicated verbatim in `TaskCreate` and `TaskUpdate`, and the comment validators added in Feature B repeated the same shape. These were extracted into shared module-level helper functions in `models.py` that each `field_validator` delegates to.

This is a pure refactor: no field name, type, default, error message, validation rule, or rule ordering changed.

**Contract that must hold identically before and after:**

| Behaviour | Expected |
| :---- | :---- |
| Blank or whitespace-only title | 422, `"Title is required and cannot be blank"` |
| Title over 200 characters | 422 |
| `due_date` as `""` or whitespace | normalized to `null`, 201/200 |
| `due_date` as `"21-07-2026"` or `"2026-02-30"` | 422 |
| `due_date` as `0` or `false` | 422 |
| `due_date` strictly before today, not Done | `is_overdue: true` |
| `due_date` equal to today | `is_overdue: false` |
| Blank or whitespace-only comment text | 422, `"Comment text is required and cannot be blank"` |
| Comment text over 1000 characters | 422 |
| Author blank, whitespace-only, or omitted | stored as `null` |
| Author over 50 characters | 422 |
| Unknown field on any request model | 422 |
| Invalid status transition | 422 |

**PASTE 5 — full suite BEFORE the refactor** (summary line only): \==================================================================== warnings summary \=====================================================================  
..\\venv\\Lib\\site-packages\\fastapi\\testclient.py:1  
  C:\\Users\\Radwan Bazzi\\Desktop\\Courses\\AI-Assisted Coding (aub)\\Task Tracker files\\task-tracker\\venv\\Lib\\site-packages\\fastapi\\testclient.py:1: StarletteDeprecationWarning: Using \`httpx\` with \`starlette.testclient\` is deprecated; install \`httpx2\` instead.  
    from starlette.testclient import TestClient as TestClient  \# noqa

\-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html  
\============================================================== 72 passed, 1 warning in 2.98s 

**PASTE 6 — full suite AFTER the refactor** (summary line only): \==================================================================== warnings summary \=====================================================================  
..\\venv\\Lib\\site-packages\\fastapi\\testclient.py:1  
  C:\\Users\\Radwan Bazzi\\Desktop\\Courses\\AI-Assisted Coding (aub)\\Task Tracker files\\task-tracker\\venv\\Lib\\site-packages\\fastapi\\testclient.py:1: StarletteDeprecationWarning: Using \`httpx\` with \`starlette.testclient\` is deprecated; install \`httpx2\` instead.  
    from starlette.testclient import TestClient as TestClient  \# noqa

\-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html  
\============================================================== 72 passed, 1 warning in 2.98s 

Both runs must show the same test count and the same result. A refactor that changes a test outcome is not a refactor — it is an undocumented behaviour change.

---

## 6\. Summary

| Requirement | Status |
| :---- | :---- |
| Baseline captured before changes | 19 passed at `e792240` |
| At least 4 new pytest tests | 53 new, 72 total |
| Both features verified in the browser | 18 API checks, 11 UI checks |
| Break Test evidence for at least 2 tests | 2 breaks plus 1 diagnosed failed attempt |
| Behaviour contract re-run after refactor | see section 5 |

