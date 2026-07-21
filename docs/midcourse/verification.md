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

=================================================================== test session starts ===================================================================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Radwan Bazzi\Desktop\Courses\AI-Assisted Coding (aub)\Task Tracker files\task-tracker\backend\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Radwan Bazzi\Desktop\Courses\AI-Assisted Coding (aub)\Task Tracker files\task-tracker\backend
plugins: anyio-4.14.1
collected 72 items                                                                                                                                         

tests/test_comments.py::test_add_comment_returns_201_with_full_body PASSED                                                                           [  1%]
tests/test_comments.py::test_add_comment_trims_surrounding_whitespace_from_text PASSED                                                               [  2%]
tests/test_comments.py::test_add_comment_without_author_stores_null_author PASSED                                                                    [  4%]
tests/test_comments.py::test_add_comment_with_whitespace_only_author_stores_null_author PASSED                                                       [  5%]
tests/test_comments.py::test_add_comment_blank_text_returns_422_with_exact_detail_message PASSED                                                     [  6%]
tests/test_comments.py::test_add_comment_whitespace_only_text_returns_422 PASSED                                                                     [  8%]
tests/test_comments.py::test_add_comment_text_over_1000_chars_returns_422 PASSED                                                                     [  9%]
tests/test_comments.py::test_add_comment_author_over_50_chars_returns_422 PASSED                                                                     [ 11%]
tests/test_comments.py::test_add_comment_unknown_field_returns_422 PASSED                                                                            [ 12%]
tests/test_comments.py::test_add_comment_to_missing_task_returns_404 PASSED                                                                          [ 13%]
tests/test_comments.py::test_list_comments_returns_all_comments_for_task PASSED                                                                      [ 15%]
tests/test_comments.py::test_list_comments_for_task_with_none_returns_200_empty_list PASSED                                                          [ 16%]
tests/test_comments.py::test_list_comments_excludes_other_tasks_comments PASSED                                                                      [ 18%]
tests/test_comments.py::test_list_comments_returns_oldest_first PASSED                                                                               [ 19%]
tests/test_comments.py::test_list_comments_for_missing_task_returns_404 PASSED                                                                       [ 20%]
tests/test_comments.py::test_delete_comment_returns_204_no_body PASSED                                                                               [ 22%]
tests/test_comments.py::test_delete_comment_removes_it_from_subsequent_list PASSED                                                                   [ 23%]
tests/test_comments.py::test_delete_missing_comment_returns_404 PASSED                                                                               [ 25%]
tests/test_comments.py::test_delete_comment_belonging_to_another_task_returns_404 PASSED                                                             [ 26%]
tests/test_comments.py::test_delete_comment_on_missing_task_returns_404 PASSED                                                                       [ 27%]
tests/test_comments.py::test_task_response_includes_comment_count_zero_by_default PASSED                                                             [ 29%]
tests/test_comments.py::test_comment_count_increases_after_adding_comment PASSED                                                                     [ 30%]
tests/test_comments.py::test_comment_count_decreases_after_deleting_comment PASSED                                                                   [ 31%]
tests/test_comments.py::test_comment_count_present_on_list_tasks_endpoint PASSED                                                                     [ 33%]
tests/test_comments.py::test_client_supplied_comment_count_returns_422 PASSED                                                                        [ 34%]
tests/test_comments.py::test_deleting_task_removes_its_comments_from_storage PASSED                                                                  [ 36%]
tests/test_comments.py::test_deleting_task_does_not_remove_other_tasks_comments PASSED                                                               [ 37%]
tests/test_due_dates.py::test_create_task_with_valid_due_date_returns_201_and_echoes_date PASSED                                                     [ 38%]
tests/test_due_dates.py::test_create_task_without_due_date_returns_201_null_date_not_overdue PASSED                                                  [ 40%]
tests/test_due_dates.py::test_create_task_with_empty_string_due_date_returns_201_null_date PASSED                                                    [ 41%]
tests/test_due_dates.py::test_create_task_with_past_due_date_returns_201_and_is_overdue_true PASSED                                                  [ 43%]
tests/test_due_dates.py::test_create_task_with_invalid_date_format_returns_422 PASSED                                                                [ 44%]
tests/test_due_dates.py::test_create_task_with_invalid_calendar_date_returns_422 PASSED                                                              [ 45%]
tests/test_due_dates.py::test_create_task_with_integer_due_date_returns_422 PASSED                                                                   [ 47%]
tests/test_due_dates.py::test_create_task_with_client_supplied_is_overdue_returns_422 PASSED                                                         [ 48%]
tests/test_due_dates.py::test_list_tasks_includes_is_overdue_on_every_task PASSED                                                                    [ 50%]
tests/test_due_dates.py::test_get_task_by_id_includes_due_date_and_is_overdue PASSED                                                                 [ 51%]
tests/test_due_dates.py::test_task_due_yesterday_and_todo_is_overdue_true PASSED                                                                     [ 52%]
tests/test_due_dates.py::test_task_due_today_is_not_overdue PASSED                                                                                   [ 54%]
tests/test_due_dates.py::test_task_due_yesterday_and_done_is_overdue_false PASSED                                                                    [ 55%]
tests/test_due_dates.py::test_patch_due_date_updates_value_returns_200 PASSED                                                                        [ 56%]
tests/test_due_dates.py::test_patch_due_date_to_future_flips_is_overdue_to_false PASSED                                                              [ 58%]
tests/test_due_dates.py::test_patch_due_date_to_null_clears_it_and_is_overdue_false PASSED                                                           [ 59%]
tests/test_due_dates.py::test_patch_omitting_due_date_leaves_existing_value_unchanged PASSED                                                         [ 61%]
tests/test_due_dates.py::test_patch_invalid_due_date_format_returns_422 PASSED                                                                       [ 62%]
tests/test_due_dates.py::test_patch_due_date_with_boolean_returns_422 PASSED                                                                         [ 63%]
tests/test_due_dates.py::test_patch_due_date_on_missing_task_returns_404 PASSED                                                                      [ 65%]
tests/test_due_dates.py::test_filter_overdue_true_returns_only_overdue_tasks PASSED                                                                  [ 66%]
tests/test_due_dates.py::test_filter_overdue_false_returns_only_non_overdue_tasks PASSED                                                             [ 68%]
tests/test_due_dates.py::test_filter_overdue_true_and_status_combines_with_and PASSED                                                                [ 69%]
tests/test_due_dates.py::test_filter_overdue_true_and_priority_combines_with_and PASSED                                                              [ 70%]
tests/test_due_dates.py::test_filter_overdue_true_and_status_done_returns_200_empty_list PASSED                                                      [ 72%]
tests/test_due_dates.py::test_filter_overdue_invalid_value_returns_422 PASSED                                                                        [ 73%]
tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body PASSED                                                                        [ 75%]
tests/test_tasks.py::test_create_task_missing_title_returns_422 PASSED                                                                               [ 76%]
tests/test_tasks.py::test_create_task_blank_title_returns_422 PASSED                                                                                 [ 77%]
tests/test_tasks.py::test_create_task_invalid_priority_returns_422 PASSED                                                                            [ 79%]
tests/test_tasks.py::test_create_task_unknown_field_returns_422 PASSED                                                                               [ 80%]
tests/test_tasks.py::test_list_tasks_empty_returns_200_and_empty_list PASSED                                                                         [ 81%]
tests/test_tasks.py::test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list PASSED                                                     [ 83%]
tests/test_tasks.py::test_list_tasks_filter_by_priority_returns_only_matches PASSED                                                                  [ 84%]
tests/test_tasks.py::test_get_task_by_id_returns_task PASSED                                                                                         [ 86%]
tests/test_tasks.py::test_get_task_by_id_not_found_returns_404_with_detail PASSED                                                                    [ 87%]
tests/test_tasks.py::test_patch_partial_update_keeps_other_fields PASSED                                                                             [ 88%]
tests/test_tasks.py::test_patch_not_found_returns_404 PASSED                                                                                         [ 90%]
tests/test_tasks.py::test_patch_valid_transition_todo_to_inprogress_returns_200 PASSED                                                               [ 91%]
tests/test_tasks.py::test_patch_existing_task_from_inprogress_to_done_returns_200 PASSED                                                             [ 93%]
tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422 PASSED                                                                   [ 94%]
tests/test_tasks.py::test_patch_existing_done_task_directly_back_to_todo_returns_422 PASSED                                                          [ 95%]
tests/test_tasks.py::test_patch_same_status_returns_422 PASSED                                                                                       [ 97%]
tests/test_tasks.py::test_delete_existing_returns_204_no_body PASSED                                                                                 [ 98%]
tests/test_tasks.py::test_delete_missing_returns_404 PASSED                                                                                          [100%]

=================================================================== 72 passed in 3.58s 

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

** post-break confirmation.** After reverting both breaks, paste the `pytest` summary line showing the suite is green again:

=================================================================== test session starts ===================================================================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Radwan Bazzi\Desktop\Courses\AI-Assisted Coding (aub)\Task Tracker files\task-tracker\backend\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Radwan Bazzi\Desktop\Courses\AI-Assisted Coding (aub)\Task Tracker files\task-tracker\backend
plugins: anyio-4.14.1
collected 72 items                                                                                                                                         

tests/test_comments.py::test_add_comment_returns_201_with_full_body PASSED                                                                           [  1%]
tests/test_comments.py::test_add_comment_trims_surrounding_whitespace_from_text PASSED                                                               [  2%]
tests/test_comments.py::test_add_comment_without_author_stores_null_author PASSED                                                                    [  4%]
tests/test_comments.py::test_add_comment_with_whitespace_only_author_stores_null_author PASSED                                                       [  5%]
tests/test_comments.py::test_add_comment_blank_text_returns_422_with_exact_detail_message PASSED                                                     [  6%]
tests/test_comments.py::test_add_comment_whitespace_only_text_returns_422 PASSED                                                                     [  8%]
tests/test_comments.py::test_add_comment_text_over_1000_chars_returns_422 PASSED                                                                     [  9%]
tests/test_comments.py::test_add_comment_author_over_50_chars_returns_422 PASSED                                                                     [ 11%]
tests/test_comments.py::test_add_comment_unknown_field_returns_422 PASSED                                                                            [ 12%]
tests/test_comments.py::test_add_comment_to_missing_task_returns_404 PASSED                                                                          [ 13%]
tests/test_comments.py::test_list_comments_returns_all_comments_for_task PASSED                                                                      [ 15%]
tests/test_comments.py::test_list_comments_for_task_with_none_returns_200_empty_list PASSED                                                          [ 16%]
tests/test_comments.py::test_list_comments_excludes_other_tasks_comments PASSED                                                                      [ 18%]
tests/test_comments.py::test_list_comments_returns_oldest_first PASSED                                                                               [ 19%]
tests/test_comments.py::test_list_comments_for_missing_task_returns_404 PASSED                                                                       [ 20%]
tests/test_comments.py::test_delete_comment_returns_204_no_body PASSED                                                                               [ 22%]
tests/test_comments.py::test_delete_comment_removes_it_from_subsequent_list PASSED                                                                   [ 23%]
tests/test_comments.py::test_delete_missing_comment_returns_404 PASSED                                                                               [ 25%]
tests/test_comments.py::test_delete_comment_belonging_to_another_task_returns_404 PASSED                                                             [ 26%]
tests/test_comments.py::test_delete_comment_on_missing_task_returns_404 PASSED                                                                       [ 27%]
tests/test_comments.py::test_task_response_includes_comment_count_zero_by_default PASSED                                                             [ 29%]
tests/test_comments.py::test_comment_count_increases_after_adding_comment PASSED                                                                     [ 30%]
tests/test_comments.py::test_comment_count_decreases_after_deleting_comment PASSED                                                                   [ 31%]
tests/test_comments.py::test_comment_count_present_on_list_tasks_endpoint PASSED                                                                     [ 33%]
tests/test_comments.py::test_client_supplied_comment_count_returns_422 PASSED                                                                        [ 34%]
tests/test_comments.py::test_deleting_task_removes_its_comments_from_storage PASSED                                                                  [ 36%]
tests/test_comments.py::test_deleting_task_does_not_remove_other_tasks_comments PASSED                                                               [ 37%]
tests/test_due_dates.py::test_create_task_with_valid_due_date_returns_201_and_echoes_date PASSED                                                     [ 38%]
tests/test_due_dates.py::test_create_task_without_due_date_returns_201_null_date_not_overdue PASSED                                                  [ 40%]
tests/test_due_dates.py::test_create_task_with_empty_string_due_date_returns_201_null_date PASSED                                                    [ 41%]
tests/test_due_dates.py::test_create_task_with_past_due_date_returns_201_and_is_overdue_true PASSED                                                  [ 43%]
tests/test_due_dates.py::test_create_task_with_invalid_date_format_returns_422 PASSED                                                                [ 44%]
tests/test_due_dates.py::test_create_task_with_invalid_calendar_date_returns_422 PASSED                                                              [ 45%]
tests/test_due_dates.py::test_create_task_with_integer_due_date_returns_422 PASSED                                                                   [ 47%]
tests/test_due_dates.py::test_create_task_with_client_supplied_is_overdue_returns_422 PASSED                                                         [ 48%]
tests/test_due_dates.py::test_list_tasks_includes_is_overdue_on_every_task PASSED                                                                    [ 50%]
tests/test_due_dates.py::test_get_task_by_id_includes_due_date_and_is_overdue PASSED                                                                 [ 51%]
tests/test_due_dates.py::test_task_due_yesterday_and_todo_is_overdue_true PASSED                                                                     [ 52%]
tests/test_due_dates.py::test_task_due_today_is_not_overdue PASSED                                                                                   [ 54%]
tests/test_due_dates.py::test_task_due_yesterday_and_done_is_overdue_false PASSED                                                                    [ 55%]
tests/test_due_dates.py::test_patch_due_date_updates_value_returns_200 PASSED                                                                        [ 56%]
tests/test_due_dates.py::test_patch_due_date_to_future_flips_is_overdue_to_false PASSED                                                              [ 58%]
tests/test_due_dates.py::test_patch_due_date_to_null_clears_it_and_is_overdue_false PASSED                                                           [ 59%]
tests/test_due_dates.py::test_patch_omitting_due_date_leaves_existing_value_unchanged PASSED                                                         [ 61%]
tests/test_due_dates.py::test_patch_invalid_due_date_format_returns_422 PASSED                                                                       [ 62%]
tests/test_due_dates.py::test_patch_due_date_with_boolean_returns_422 PASSED                                                                         [ 63%]
tests/test_due_dates.py::test_patch_due_date_on_missing_task_returns_404 PASSED                                                                      [ 65%]
tests/test_due_dates.py::test_filter_overdue_true_returns_only_overdue_tasks PASSED                                                                  [ 66%]
tests/test_due_dates.py::test_filter_overdue_false_returns_only_non_overdue_tasks PASSED                                                             [ 68%]
tests/test_due_dates.py::test_filter_overdue_true_and_status_combines_with_and PASSED                                                                [ 69%]
tests/test_due_dates.py::test_filter_overdue_true_and_priority_combines_with_and PASSED                                                              [ 70%]
tests/test_due_dates.py::test_filter_overdue_true_and_status_done_returns_200_empty_list PASSED                                                      [ 72%]
tests/test_due_dates.py::test_filter_overdue_invalid_value_returns_422 PASSED                                                                        [ 73%]
tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body PASSED                                                                        [ 75%]
tests/test_tasks.py::test_create_task_missing_title_returns_422 PASSED                                                                               [ 76%]
tests/test_tasks.py::test_create_task_blank_title_returns_422 PASSED                                                                                 [ 77%]
tests/test_tasks.py::test_create_task_invalid_priority_returns_422 PASSED                                                                            [ 79%]
tests/test_tasks.py::test_create_task_unknown_field_returns_422 PASSED                                                                               [ 80%]
tests/test_tasks.py::test_list_tasks_empty_returns_200_and_empty_list PASSED                                                                         [ 81%]
tests/test_tasks.py::test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list PASSED                                                     [ 83%]
tests/test_tasks.py::test_list_tasks_filter_by_priority_returns_only_matches PASSED                                                                  [ 84%]
tests/test_tasks.py::test_get_task_by_id_returns_task PASSED                                                                                         [ 86%]
tests/test_tasks.py::test_get_task_by_id_not_found_returns_404_with_detail PASSED                                                                    [ 87%]
tests/test_tasks.py::test_patch_partial_update_keeps_other_fields PASSED                                                                             [ 88%]
tests/test_tasks.py::test_patch_not_found_returns_404 PASSED                                                                                         [ 90%]
tests/test_tasks.py::test_patch_valid_transition_todo_to_inprogress_returns_200 PASSED                                                               [ 91%]
tests/test_tasks.py::test_patch_existing_task_from_inprogress_to_done_returns_200 PASSED                                                             [ 93%]
tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422 PASSED                                                                   [ 94%]
tests/test_tasks.py::test_patch_existing_done_task_directly_back_to_todo_returns_422 PASSED                                                          [ 95%]
tests/test_tasks.py::test_patch_same_status_returns_422 PASSED                                                                                       [ 97%]
tests/test_tasks.py::test_delete_existing_returns_204_no_body PASSED                                                                                 [ 98%]
tests/test_tasks.py::test_delete_missing_returns_404 PASSED                                                                                          [100%]

=================================================================== 72 passed in 3.58s 

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

**PASTE 5 — full suite BEFORE the refactor**=================================================================== test session starts ===================================================================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Radwan Bazzi\Desktop\Courses\AI-Assisted Coding (aub)\Task Tracker files\task-tracker\backend\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Radwan Bazzi\Desktop\Courses\AI-Assisted Coding (aub)\Task Tracker files\task-tracker\backend
plugins: anyio-4.14.1
collected 72 items                                                                                                                                         

tests/test_comments.py::test_add_comment_returns_201_with_full_body PASSED                                                                           [  1%]
tests/test_comments.py::test_add_comment_trims_surrounding_whitespace_from_text PASSED                                                               [  2%]
tests/test_comments.py::test_add_comment_without_author_stores_null_author PASSED                                                                    [  4%]
tests/test_comments.py::test_add_comment_with_whitespace_only_author_stores_null_author PASSED                                                       [  5%]
tests/test_comments.py::test_add_comment_blank_text_returns_422_with_exact_detail_message PASSED                                                     [  6%]
tests/test_comments.py::test_add_comment_whitespace_only_text_returns_422 PASSED                                                                     [  8%]
tests/test_comments.py::test_add_comment_text_over_1000_chars_returns_422 PASSED                                                                     [  9%]
tests/test_comments.py::test_add_comment_author_over_50_chars_returns_422 PASSED                                                                     [ 11%]
tests/test_comments.py::test_add_comment_unknown_field_returns_422 PASSED                                                                            [ 12%]
tests/test_comments.py::test_add_comment_to_missing_task_returns_404 PASSED                                                                          [ 13%]
tests/test_comments.py::test_list_comments_returns_all_comments_for_task PASSED                                                                      [ 15%]
tests/test_comments.py::test_list_comments_for_task_with_none_returns_200_empty_list PASSED                                                          [ 16%]
tests/test_comments.py::test_list_comments_excludes_other_tasks_comments PASSED                                                                      [ 18%]
tests/test_comments.py::test_list_comments_returns_oldest_first PASSED                                                                               [ 19%]
tests/test_comments.py::test_list_comments_for_missing_task_returns_404 PASSED                                                                       [ 20%]
tests/test_comments.py::test_delete_comment_returns_204_no_body PASSED                                                                               [ 22%]
tests/test_comments.py::test_delete_comment_removes_it_from_subsequent_list PASSED                                                                   [ 23%]
tests/test_comments.py::test_delete_missing_comment_returns_404 PASSED                                                                               [ 25%]
tests/test_comments.py::test_delete_comment_belonging_to_another_task_returns_404 PASSED                                                             [ 26%]
tests/test_comments.py::test_delete_comment_on_missing_task_returns_404 PASSED                                                                       [ 27%]
tests/test_comments.py::test_task_response_includes_comment_count_zero_by_default PASSED                                                             [ 29%]
tests/test_comments.py::test_comment_count_increases_after_adding_comment PASSED                                                                     [ 30%]
tests/test_comments.py::test_comment_count_decreases_after_deleting_comment PASSED                                                                   [ 31%]
tests/test_comments.py::test_comment_count_present_on_list_tasks_endpoint PASSED                                                                     [ 33%]
tests/test_comments.py::test_client_supplied_comment_count_returns_422 PASSED                                                                        [ 34%]
tests/test_comments.py::test_deleting_task_removes_its_comments_from_storage PASSED                                                                  [ 36%]
tests/test_comments.py::test_deleting_task_does_not_remove_other_tasks_comments PASSED                                                               [ 37%]
tests/test_due_dates.py::test_create_task_with_valid_due_date_returns_201_and_echoes_date PASSED                                                     [ 38%]
tests/test_due_dates.py::test_create_task_without_due_date_returns_201_null_date_not_overdue PASSED                                                  [ 40%]
tests/test_due_dates.py::test_create_task_with_empty_string_due_date_returns_201_null_date PASSED                                                    [ 41%]
tests/test_due_dates.py::test_create_task_with_past_due_date_returns_201_and_is_overdue_true PASSED                                                  [ 43%]
tests/test_due_dates.py::test_create_task_with_invalid_date_format_returns_422 PASSED                                                                [ 44%]
tests/test_due_dates.py::test_create_task_with_invalid_calendar_date_returns_422 PASSED                                                              [ 45%]
tests/test_due_dates.py::test_create_task_with_integer_due_date_returns_422 PASSED                                                                   [ 47%]
tests/test_due_dates.py::test_create_task_with_client_supplied_is_overdue_returns_422 PASSED                                                         [ 48%]
tests/test_due_dates.py::test_list_tasks_includes_is_overdue_on_every_task PASSED                                                                    [ 50%]
tests/test_due_dates.py::test_get_task_by_id_includes_due_date_and_is_overdue PASSED                                                                 [ 51%]
tests/test_due_dates.py::test_task_due_yesterday_and_todo_is_overdue_true PASSED                                                                     [ 52%]
tests/test_due_dates.py::test_task_due_today_is_not_overdue PASSED                                                                                   [ 54%]
tests/test_due_dates.py::test_task_due_yesterday_and_done_is_overdue_false PASSED                                                                    [ 55%]
tests/test_due_dates.py::test_patch_due_date_updates_value_returns_200 PASSED                                                                        [ 56%]
tests/test_due_dates.py::test_patch_due_date_to_future_flips_is_overdue_to_false PASSED                                                              [ 58%]
tests/test_due_dates.py::test_patch_due_date_to_null_clears_it_and_is_overdue_false PASSED                                                           [ 59%]
tests/test_due_dates.py::test_patch_omitting_due_date_leaves_existing_value_unchanged PASSED                                                         [ 61%]
tests/test_due_dates.py::test_patch_invalid_due_date_format_returns_422 PASSED                                                                       [ 62%]
tests/test_due_dates.py::test_patch_due_date_with_boolean_returns_422 PASSED                                                                         [ 63%]
tests/test_due_dates.py::test_patch_due_date_on_missing_task_returns_404 PASSED                                                                      [ 65%]
tests/test_due_dates.py::test_filter_overdue_true_returns_only_overdue_tasks PASSED                                                                  [ 66%]
tests/test_due_dates.py::test_filter_overdue_false_returns_only_non_overdue_tasks PASSED                                                             [ 68%]
tests/test_due_dates.py::test_filter_overdue_true_and_status_combines_with_and PASSED                                                                [ 69%]
tests/test_due_dates.py::test_filter_overdue_true_and_priority_combines_with_and PASSED                                                              [ 70%]
tests/test_due_dates.py::test_filter_overdue_true_and_status_done_returns_200_empty_list PASSED                                                      [ 72%]
tests/test_due_dates.py::test_filter_overdue_invalid_value_returns_422 PASSED                                                                        [ 73%]
tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body PASSED                                                                        [ 75%]
tests/test_tasks.py::test_create_task_missing_title_returns_422 PASSED                                                                               [ 76%]
tests/test_tasks.py::test_create_task_blank_title_returns_422 PASSED                                                                                 [ 77%]
tests/test_tasks.py::test_create_task_invalid_priority_returns_422 PASSED                                                                            [ 79%]
tests/test_tasks.py::test_create_task_unknown_field_returns_422 PASSED                                                                               [ 80%]
tests/test_tasks.py::test_list_tasks_empty_returns_200_and_empty_list PASSED                                                                         [ 81%]
tests/test_tasks.py::test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list PASSED                                                     [ 83%]
tests/test_tasks.py::test_list_tasks_filter_by_priority_returns_only_matches PASSED                                                                  [ 84%]
tests/test_tasks.py::test_get_task_by_id_returns_task PASSED                                                                                         [ 86%]
tests/test_tasks.py::test_get_task_by_id_not_found_returns_404_with_detail PASSED                                                                    [ 87%]
tests/test_tasks.py::test_patch_partial_update_keeps_other_fields PASSED                                                                             [ 88%]
tests/test_tasks.py::test_patch_not_found_returns_404 PASSED                                                                                         [ 90%]
tests/test_tasks.py::test_patch_valid_transition_todo_to_inprogress_returns_200 PASSED                                                               [ 91%]
tests/test_tasks.py::test_patch_existing_task_from_inprogress_to_done_returns_200 PASSED                                                             [ 93%]
tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422 PASSED                                                                   [ 94%]
tests/test_tasks.py::test_patch_existing_done_task_directly_back_to_todo_returns_422 PASSED                                                          [ 95%]
tests/test_tasks.py::test_patch_same_status_returns_422 PASSED                                                                                       [ 97%]
tests/test_tasks.py::test_delete_existing_returns_204_no_body PASSED                                                                                 [ 98%]
tests/test_tasks.py::test_delete_missing_returns_404 PASSED                                                                                          [100%]

=================================================================== 72 passed in 2.20s ====================================================================
(venv) PS C:\Users\Radwan Bazzi\Desktop\Courses\AI-Assisted Coding (aub)\Task Tracker files\task-tracker\backend> cd ..
>> git stash list    # just checking
>> git show 4ac2cfb:backend/app/models.py > $env:TEMP\models_before.py
(venv) PS C:\Users\Radwan Bazzi\Desktop\Courses\AI-Assisted Coding (aub)\Task Tracker files\task-tracker> cd "C:\Users\Radwan Bazzi\Desktop\Courses\AI-Assisted Coding (aub)\Task Tracker files\task-tracker\backend"
>> .\venv\Scripts\activate                                            
>> pytest -v
=================================================================== test session starts ===================================================================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Radwan Bazzi\Desktop\Courses\AI-Assisted Coding (aub)\Task Tracker files\task-tracker\backend\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Radwan Bazzi\Desktop\Courses\AI-Assisted Coding (aub)\Task Tracker files\task-tracker\backend
plugins: anyio-4.14.1
collected 72 items                                                                                                                                         

tests/test_comments.py::test_add_comment_returns_201_with_full_body PASSED                                                                           [  1%]
tests/test_comments.py::test_add_comment_trims_surrounding_whitespace_from_text PASSED                                                               [  2%]
tests/test_comments.py::test_add_comment_without_author_stores_null_author PASSED                                                                    [  4%]
tests/test_comments.py::test_add_comment_with_whitespace_only_author_stores_null_author PASSED                                                       [  5%]
tests/test_comments.py::test_add_comment_blank_text_returns_422_with_exact_detail_message PASSED                                                     [  6%]
tests/test_comments.py::test_add_comment_whitespace_only_text_returns_422 PASSED                                                                     [  8%]
tests/test_comments.py::test_add_comment_text_over_1000_chars_returns_422 PASSED                                                                     [  9%]
tests/test_comments.py::test_add_comment_author_over_50_chars_returns_422 PASSED                                                                     [ 11%]
tests/test_comments.py::test_add_comment_unknown_field_returns_422 PASSED                                                                            [ 12%]
tests/test_comments.py::test_add_comment_to_missing_task_returns_404 PASSED                                                                          [ 13%]
tests/test_comments.py::test_list_comments_returns_all_comments_for_task PASSED                                                                      [ 15%]
tests/test_comments.py::test_list_comments_for_task_with_none_returns_200_empty_list PASSED                                                          [ 16%]
tests/test_comments.py::test_list_comments_excludes_other_tasks_comments PASSED                                                                      [ 18%]
tests/test_comments.py::test_list_comments_returns_oldest_first PASSED                                                                               [ 19%]
tests/test_comments.py::test_list_comments_for_missing_task_returns_404 PASSED                                                                       [ 20%]
tests/test_comments.py::test_delete_comment_returns_204_no_body PASSED                                                                               [ 22%]
tests/test_comments.py::test_delete_comment_removes_it_from_subsequent_list PASSED                                                                   [ 23%]
tests/test_comments.py::test_delete_missing_comment_returns_404 PASSED                                                                               [ 25%]
tests/test_comments.py::test_delete_comment_belonging_to_another_task_returns_404 PASSED                                                             [ 26%]
tests/test_comments.py::test_delete_comment_on_missing_task_returns_404 PASSED                                                                       [ 27%]
tests/test_comments.py::test_task_response_includes_comment_count_zero_by_default PASSED                                                             [ 29%]
tests/test_comments.py::test_comment_count_increases_after_adding_comment PASSED                                                                     [ 30%]
tests/test_comments.py::test_comment_count_decreases_after_deleting_comment PASSED                                                                   [ 31%]
tests/test_comments.py::test_comment_count_present_on_list_tasks_endpoint PASSED                                                                     [ 33%]
tests/test_comments.py::test_client_supplied_comment_count_returns_422 PASSED                                                                        [ 34%]
tests/test_comments.py::test_deleting_task_removes_its_comments_from_storage PASSED                                                                  [ 36%]
tests/test_comments.py::test_deleting_task_does_not_remove_other_tasks_comments PASSED                                                               [ 37%]
tests/test_due_dates.py::test_create_task_with_valid_due_date_returns_201_and_echoes_date PASSED                                                     [ 38%]
tests/test_due_dates.py::test_create_task_without_due_date_returns_201_null_date_not_overdue PASSED                                                  [ 40%]
tests/test_due_dates.py::test_create_task_with_empty_string_due_date_returns_201_null_date PASSED                                                    [ 41%]
tests/test_due_dates.py::test_create_task_with_past_due_date_returns_201_and_is_overdue_true PASSED                                                  [ 43%]
tests/test_due_dates.py::test_create_task_with_invalid_date_format_returns_422 PASSED                                                                [ 44%]
tests/test_due_dates.py::test_create_task_with_invalid_calendar_date_returns_422 PASSED                                                              [ 45%]
tests/test_due_dates.py::test_create_task_with_integer_due_date_returns_422 PASSED                                                                   [ 47%]
tests/test_due_dates.py::test_create_task_with_client_supplied_is_overdue_returns_422 PASSED                                                         [ 48%]
tests/test_due_dates.py::test_list_tasks_includes_is_overdue_on_every_task PASSED                                                                    [ 50%]
tests/test_due_dates.py::test_get_task_by_id_includes_due_date_and_is_overdue PASSED                                                                 [ 51%]
tests/test_due_dates.py::test_task_due_yesterday_and_todo_is_overdue_true PASSED                                                                     [ 52%]
tests/test_due_dates.py::test_task_due_today_is_not_overdue PASSED                                                                                   [ 54%]
tests/test_due_dates.py::test_task_due_yesterday_and_done_is_overdue_false PASSED                                                                    [ 55%]
tests/test_due_dates.py::test_patch_due_date_updates_value_returns_200 PASSED                                                                        [ 56%]
tests/test_due_dates.py::test_patch_due_date_to_future_flips_is_overdue_to_false PASSED                                                              [ 58%]
tests/test_due_dates.py::test_patch_due_date_to_null_clears_it_and_is_overdue_false PASSED                                                           [ 59%]
tests/test_due_dates.py::test_patch_omitting_due_date_leaves_existing_value_unchanged PASSED                                                         [ 61%]
tests/test_due_dates.py::test_patch_invalid_due_date_format_returns_422 PASSED                                                                       [ 62%]
tests/test_due_dates.py::test_patch_due_date_with_boolean_returns_422 PASSED                                                                         [ 63%]
tests/test_due_dates.py::test_patch_due_date_on_missing_task_returns_404 PASSED                                                                      [ 65%]
tests/test_due_dates.py::test_filter_overdue_true_returns_only_overdue_tasks PASSED                                                                  [ 66%]
tests/test_due_dates.py::test_filter_overdue_false_returns_only_non_overdue_tasks PASSED                                                             [ 68%]
tests/test_due_dates.py::test_filter_overdue_true_and_status_combines_with_and PASSED                                                                [ 69%]
tests/test_due_dates.py::test_filter_overdue_true_and_priority_combines_with_and PASSED                                                              [ 70%]
tests/test_due_dates.py::test_filter_overdue_true_and_status_done_returns_200_empty_list PASSED                                                      [ 72%]
tests/test_due_dates.py::test_filter_overdue_invalid_value_returns_422 PASSED                                                                        [ 73%]
tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body PASSED                                                                        [ 75%]
tests/test_tasks.py::test_create_task_missing_title_returns_422 PASSED                                                                               [ 76%]
tests/test_tasks.py::test_create_task_blank_title_returns_422 PASSED                                                                                 [ 77%]
tests/test_tasks.py::test_create_task_invalid_priority_returns_422 PASSED                                                                            [ 79%]
tests/test_tasks.py::test_create_task_unknown_field_returns_422 PASSED                                                                               [ 80%]
tests/test_tasks.py::test_list_tasks_empty_returns_200_and_empty_list PASSED                                                                         [ 81%]
tests/test_tasks.py::test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list PASSED                                                     [ 83%]
tests/test_tasks.py::test_list_tasks_filter_by_priority_returns_only_matches PASSED                                                                  [ 84%]
tests/test_tasks.py::test_get_task_by_id_returns_task PASSED                                                                                         [ 86%]
tests/test_tasks.py::test_get_task_by_id_not_found_returns_404_with_detail PASSED                                                                    [ 87%]
tests/test_tasks.py::test_patch_partial_update_keeps_other_fields PASSED                                                                             [ 88%]
tests/test_tasks.py::test_patch_not_found_returns_404 PASSED                                                                                         [ 90%]
tests/test_tasks.py::test_patch_valid_transition_todo_to_inprogress_returns_200 PASSED                                                               [ 91%]
tests/test_tasks.py::test_patch_existing_task_from_inprogress_to_done_returns_200 PASSED                                                             [ 93%]
tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422 PASSED                                                                   [ 94%]
tests/test_tasks.py::test_patch_existing_done_task_directly_back_to_todo_returns_422 PASSED                                                          [ 95%]
tests/test_tasks.py::test_patch_same_status_returns_422 PASSED                                                                                       [ 97%]
tests/test_tasks.py::test_delete_existing_returns_204_no_body PASSED                                                                                 [ 98%]
tests/test_tasks.py::test_delete_missing_returns_404 PASSED                                                                                          [100%]

=================================================================== 72 passed in 1.90s

**PASTE 6 — full suite AFTER the refactor** =================================================================== test session starts ===================================================================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Radwan Bazzi\Desktop\Courses\AI-Assisted Coding (aub)\Task Tracker files\task-tracker\backend\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Radwan Bazzi\Desktop\Courses\AI-Assisted Coding (aub)\Task Tracker files\task-tracker\backend
plugins: anyio-4.14.1
collected 72 items                                                                                                                                         

tests/test_comments.py::test_add_comment_returns_201_with_full_body PASSED                                                                           [  1%]
tests/test_comments.py::test_add_comment_trims_surrounding_whitespace_from_text PASSED                                                               [  2%]
tests/test_comments.py::test_add_comment_without_author_stores_null_author PASSED                                                                    [  4%]
tests/test_comments.py::test_add_comment_with_whitespace_only_author_stores_null_author PASSED                                                       [  5%]
tests/test_comments.py::test_add_comment_blank_text_returns_422_with_exact_detail_message PASSED                                                     [  6%]
tests/test_comments.py::test_add_comment_whitespace_only_text_returns_422 PASSED                                                                     [  8%]
tests/test_comments.py::test_add_comment_text_over_1000_chars_returns_422 PASSED                                                                     [  9%]
tests/test_comments.py::test_add_comment_author_over_50_chars_returns_422 PASSED                                                                     [ 11%]
tests/test_comments.py::test_add_comment_unknown_field_returns_422 PASSED                                                                            [ 12%]
tests/test_comments.py::test_add_comment_to_missing_task_returns_404 PASSED                                                                          [ 13%]
tests/test_comments.py::test_list_comments_returns_all_comments_for_task PASSED                                                                      [ 15%]
tests/test_comments.py::test_list_comments_for_task_with_none_returns_200_empty_list PASSED                                                          [ 16%]
tests/test_comments.py::test_list_comments_excludes_other_tasks_comments PASSED                                                                      [ 18%]
tests/test_comments.py::test_list_comments_returns_oldest_first PASSED                                                                               [ 19%]
tests/test_comments.py::test_list_comments_for_missing_task_returns_404 PASSED                                                                       [ 20%]
tests/test_comments.py::test_delete_comment_returns_204_no_body PASSED                                                                               [ 22%]
tests/test_comments.py::test_delete_comment_removes_it_from_subsequent_list PASSED                                                                   [ 23%]
tests/test_comments.py::test_delete_missing_comment_returns_404 PASSED                                                                               [ 25%]
tests/test_comments.py::test_delete_comment_belonging_to_another_task_returns_404 PASSED                                                             [ 26%]
tests/test_comments.py::test_delete_comment_on_missing_task_returns_404 PASSED                                                                       [ 27%]
tests/test_comments.py::test_task_response_includes_comment_count_zero_by_default PASSED                                                             [ 29%]
tests/test_comments.py::test_comment_count_increases_after_adding_comment PASSED                                                                     [ 30%]
tests/test_comments.py::test_comment_count_decreases_after_deleting_comment PASSED                                                                   [ 31%]
tests/test_comments.py::test_comment_count_present_on_list_tasks_endpoint PASSED                                                                     [ 33%]
tests/test_comments.py::test_client_supplied_comment_count_returns_422 PASSED                                                                        [ 34%]
tests/test_comments.py::test_deleting_task_removes_its_comments_from_storage PASSED                                                                  [ 36%]
tests/test_comments.py::test_deleting_task_does_not_remove_other_tasks_comments PASSED                                                               [ 37%]
tests/test_due_dates.py::test_create_task_with_valid_due_date_returns_201_and_echoes_date PASSED                                                     [ 38%]
tests/test_due_dates.py::test_create_task_without_due_date_returns_201_null_date_not_overdue PASSED                                                  [ 40%]
tests/test_due_dates.py::test_create_task_with_empty_string_due_date_returns_201_null_date PASSED                                                    [ 41%]
tests/test_due_dates.py::test_create_task_with_past_due_date_returns_201_and_is_overdue_true PASSED                                                  [ 43%]
tests/test_due_dates.py::test_create_task_with_invalid_date_format_returns_422 PASSED                                                                [ 44%]
tests/test_due_dates.py::test_create_task_with_invalid_calendar_date_returns_422 PASSED                                                              [ 45%]
tests/test_due_dates.py::test_create_task_with_integer_due_date_returns_422 PASSED                                                                   [ 47%]
tests/test_due_dates.py::test_create_task_with_client_supplied_is_overdue_returns_422 PASSED                                                         [ 48%]
tests/test_due_dates.py::test_list_tasks_includes_is_overdue_on_every_task PASSED                                                                    [ 50%]
tests/test_due_dates.py::test_get_task_by_id_includes_due_date_and_is_overdue PASSED                                                                 [ 51%]
tests/test_due_dates.py::test_task_due_yesterday_and_todo_is_overdue_true PASSED                                                                     [ 52%]
tests/test_due_dates.py::test_task_due_today_is_not_overdue PASSED                                                                                   [ 54%]
tests/test_due_dates.py::test_task_due_yesterday_and_done_is_overdue_false PASSED                                                                    [ 55%]
tests/test_due_dates.py::test_patch_due_date_updates_value_returns_200 PASSED                                                                        [ 56%]
tests/test_due_dates.py::test_patch_due_date_to_future_flips_is_overdue_to_false PASSED                                                              [ 58%]
tests/test_due_dates.py::test_patch_due_date_to_null_clears_it_and_is_overdue_false PASSED                                                           [ 59%]
tests/test_due_dates.py::test_patch_omitting_due_date_leaves_existing_value_unchanged PASSED                                                         [ 61%]
tests/test_due_dates.py::test_patch_invalid_due_date_format_returns_422 PASSED                                                                       [ 62%]
tests/test_due_dates.py::test_patch_due_date_with_boolean_returns_422 PASSED                                                                         [ 63%]
tests/test_due_dates.py::test_patch_due_date_on_missing_task_returns_404 PASSED                                                                      [ 65%]
tests/test_due_dates.py::test_filter_overdue_true_returns_only_overdue_tasks PASSED                                                                  [ 66%]
tests/test_due_dates.py::test_filter_overdue_false_returns_only_non_overdue_tasks PASSED                                                             [ 68%]
tests/test_due_dates.py::test_filter_overdue_true_and_status_combines_with_and PASSED                                                                [ 69%]
tests/test_due_dates.py::test_filter_overdue_true_and_priority_combines_with_and PASSED                                                              [ 70%]
tests/test_due_dates.py::test_filter_overdue_true_and_status_done_returns_200_empty_list PASSED                                                      [ 72%]
tests/test_due_dates.py::test_filter_overdue_invalid_value_returns_422 PASSED                                                                        [ 73%]
tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body PASSED                                                                        [ 75%]
tests/test_tasks.py::test_create_task_missing_title_returns_422 PASSED                                                                               [ 76%]
tests/test_tasks.py::test_create_task_blank_title_returns_422 PASSED                                                                                 [ 77%]
tests/test_tasks.py::test_create_task_invalid_priority_returns_422 PASSED                                                                            [ 79%]
tests/test_tasks.py::test_create_task_unknown_field_returns_422 PASSED                                                                               [ 80%]
tests/test_tasks.py::test_list_tasks_empty_returns_200_and_empty_list PASSED                                                                         [ 81%]
tests/test_tasks.py::test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list PASSED                                                     [ 83%]
tests/test_tasks.py::test_list_tasks_filter_by_priority_returns_only_matches PASSED                                                                  [ 84%]
tests/test_tasks.py::test_get_task_by_id_returns_task PASSED                                                                                         [ 86%]
tests/test_tasks.py::test_get_task_by_id_not_found_returns_404_with_detail PASSED                                                                    [ 87%]
tests/test_tasks.py::test_patch_partial_update_keeps_other_fields PASSED                                                                             [ 88%]
tests/test_tasks.py::test_patch_not_found_returns_404 PASSED                                                                                         [ 90%]
tests/test_tasks.py::test_patch_valid_transition_todo_to_inprogress_returns_200 PASSED                                                               [ 91%]
tests/test_tasks.py::test_patch_existing_task_from_inprogress_to_done_returns_200 PASSED                                                             [ 93%]
tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422 PASSED                                                                   [ 94%]
tests/test_tasks.py::test_patch_existing_done_task_directly_back_to_todo_returns_422 PASSED                                                          [ 95%]
tests/test_tasks.py::test_patch_same_status_returns_422 PASSED                                                                                       [ 97%]
tests/test_tasks.py::test_delete_existing_returns_204_no_body PASSED                                                                                 [ 98%]
tests/test_tasks.py::test_delete_missing_returns_404 PASSED                                                                                          [100%]

=================================================================== 72 passed in 3.58s 

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

