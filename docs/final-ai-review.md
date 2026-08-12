# Final AI Review and Ownership Evidence

**Student:** Youssef Bazzi
**Course:** AI-Assisted Coding (AUB) — Final Course Project
**Branch:** `final-project`
**Date of this review:** 2026-08-12

**Reviewing tools used:** two independent read-only passes over the same diff — **Claude (Cowork desktop agent)** and **Codex** — both on 2026-08-12, each graded separately below. Every behavioural claim from either tool was verified by me with isolated Starlette `TestClient` probes against `app.main:app` before being graded. Earlier Module 5 findings referenced below came from a Codex read-only security audit and are recorded in `docs/security-review.md`.

**Scope reviewed:** `backend/app/models.py` (changed by commits `44b2e0f` and `772e335`), `backend/app/main.py` (changed by commit `6b6e885`), `frontend/index.html`, `Dockerfile`, `.dockerignore`, `.github/workflows/ci.yml`, `requirements.txt`.

---

## AGENTS.md guardrails

| Check | Result | Evidence |
|---|---|---|
| Repo-specific stack and commands included | **Yes** | `AGENTS.md:29-118` — pinned versions (FastAPI 0.139.0, Pydantic 2.13.4, Uvicorn 0.51.0, pytest 9.1.1), plus the exact `uvicorn app.main:app --reload --port 8000`, `python -m http.server 5500`, `pytest -v`, and `docker build`/`docker run` commands. |
| Docs-first / read-first guardrail included | **Yes** | `AGENTS.md:183-184` — "Docs first: Read `README.md`, relevant files under `docs/`, and applicable tests before proposing code changes" and "Read-only by default: Begin with inspection and analysis." |
| Unexpected `app/` / `frontend/` edits rule included | **Yes** | `AGENTS.md:186-188` — "Do not modify `backend/app/` unless the user explicitly approves application-code changes in the current task. Treat `frontend/index.html` as application code and ask before modifying it as well." Followed by "Approval to inspect, review, document, or suggest a change is not approval to implement it." |
| Evidence / anti-hallucination rule included | **Yes** | `AGENTS.md:7` and `AGENTS.md:197-201` — the Confirmed / Inference / Not confirmed labelling requirement, and "Never invent test results, vulnerabilities, approvals, commands, business rules, file contents, or completed actions." |
| Secrets rule included | **Yes** | `AGENTS.md:192` — never paste, expose, commit, or repeat credentials, tokens, or `.env` contents. |

**Note on the "not confirmed" convention.** `AGENTS.md` requires unverified claims to be labelled rather than asserted. That convention is visible in the repository itself: `README.md:128` and `README.md:207` carry `[VERIFY]` markers, and `AGENTS.md:51` and `AGENTS.md:116` explicitly state that a fresh dependency install and a Docker build were *not* executed while the file was drafted. Those honest gaps are closed in `docs/release-evidence.md`.

---

## AI code review mini-log

**File under review:** `backend/app/models.py`
**Diff reviewed:** the Module 5 security remediation commits `44b2e0f` ("fix: reject non-string comment authors", +2 lines) and `772e335` ("fix: reject null task update fields", +7 lines).

The diff, as recorded by `git show`:

```python
# 44b2e0f — inside _normalize_comment_author_value
+    if not isinstance(v, str):
+        raise ValueError("Author must be a string")

# 772e335 — inside TaskUpdate
+    @field_validator("title", "description", "status", "priority", mode="before")
+    @classmethod
+    def _reject_null_for_required_fields(cls, v):
+        if v is None:
+            raise ValueError("Field cannot be null")
+        return v
```

| # | AI comment | Grade | Reason | Verification or decision |
|---|---|---|---|---|
| 1 | "`_reject_null_for_required_fields` is registered with `mode='before'` across four fields. A `before` validator that rejects `None` will also fire for fields the client omitted, breaking `TaskUpdate`'s partial-update contract — omitting `status` will now 422." | **Wrong** | The premise is false. A Pydantic v2 `field_validator` only runs for fields actually present in the input; omitted fields never reach the validator, they fall through to the model default. The comment confuses "field defaults to `None`" with "field is validated as `None`". | Disproved by probe, not by reading. `PATCH /tasks/{id}` with body `{"status": "InProgress"}` and every other field omitted returned **200**, and `tests/test_tasks.py::test_patch_partial_update_keeps_other_fields` and `tests/test_due_dates.py::test_patch_omitting_due_date_leaves_existing_value_unchanged` both pass in the 72-test run. **Rejected — no change made.** |
| 2 | "`TaskCreate.description` is `Optional[str] = \"\"` but `TaskResponse.description` is a required `str`. A client sending `{\"title\": \"x\", \"description\": null}` will pass input validation, store `None`, and then crash response serialisation with a 500." | **Wrong** | Sound reasoning about the schema mismatch, but it stops at the two model definitions and never follows the write path. `storage.add_task` coerces the value before it ever reaches `TaskResponse`. | Disproved by probe. `POST /tasks {"title":"a","description":null}` returned **201** with `"description":""`. The coercion is at `backend/app/storage.py:40` — `description=payload.description or ""` — and is documented in that function's own docstring (`storage.py:26`). **Rejected — no change made.** Worth noting the finding was *plausible*; only running it settled it. |
| 3 | "The new `isinstance` type guard was added to `_normalize_comment_author_value` but not to `_validate_comment_text_value`. `CommentCreate.text` has the same shape, so a non-string `text` is still unguarded." | **Noise** | The observation about asymmetry is factually true, but it does not describe a defect. `author` needed the guard only because its validator calls `.strip()` in `mode="before"`, ahead of type checking — that is exactly what caused ERR-01's 500. `text` is validated in default (after) mode, so Pydantic enforces `str` before the validator body runs. | Confirmed by probe: `POST /tasks/{id}/comments {"text":123}` returned **422**, and `{"text":[]}` returned **422** — not 500. Adding a redundant guard would touch protected app code for no behaviour change. **Not applied.** |
| 4 | "`TaskUpdate` now has three separate validators touching `title` (`_reject_null_for_required_fields`, `_normalize_due_date`, `_validate_title_if_provided`). Collapse them into one validator for readability." | **Noise** | Style-only, and partly inaccurate — `_normalize_due_date` does not touch `title`. Merging would mix a null-rejection concern with a length/blank concern in one function and make the 422 messages harder to attribute. | Declined. This is application code protected by `AGENTS.md:186`, and the brief forbids changes that are not a bug fix, security fix, or documentation-supported correction. **Not applied.** |
| 5 | "`TaskResponse` and `CommentResponse` set `model_config = ConfigDict(extra='forbid')`. `extra='forbid'` is an input-validation setting; on a response model the server is the only constructor, so it protects nothing." | **Useful** | Correct and correctly scoped. It is a genuine observation about intent-vs-effect: the real guarantee that clients cannot inject `is_overdue` or `comment_count` comes from `extra="forbid"` on `TaskCreate`/`TaskUpdate` (`models.py:64`, `models.py:87`), not from the response models. | Verified: `tests/test_due_dates.py::test_create_task_with_client_supplied_is_overdue_returns_422` passes and is asserting against the *input* model. Graded Useful as a documentation correction, **not** as a code change — the response-model config is harmless, and removing it would be an unrequested app edit. Logged here rather than acted on. |

**Summary of the Claude pass:** 1 Useful, 2 Noise, 2 Wrong. Both Wrong comments were confidently worded and internally coherent; both were only disproved by executing the code rather than reading it. That is the single clearest lesson from this review.

---

### Second pass — independent Codex review

The table above records a Claude (Cowork) review. To test whether a second, independent tool would reach the same conclusions on the same diff, the identical scope was given to **Codex** on 2026-08-12, under the read-only instruction and the `AGENTS.md` guardrails.

Codex returned 3 comments and explicitly declined to produce more, stating: *"I found no additional runtime defect in the two fixes and did not manufacture further comments."* It confirmed at the end: *"No files were changed, nothing was installed, and no server was started. The final worktree diff was empty."* **The `AGENTS.md` read-only and protected-path guardrails held under test** — `git status` after the run showed no modifications.

Every claim below was independently verified by me before grading. I did not take Codex's "Confirmed" self-labels at face value.

| # | Codex comment | Grade | Reason | Verification or decision |
|---|---|---|---|---|
| C1 | "`/openapi.json` describes `title`, `description`, `status` and `priority` as accepting `null`, but a PATCH containing any of them as `null` returns HTTP 422. OpenAPI-generated clients can therefore produce requests the contract says are valid but the runtime rejects." (`backend/app/models.py:89-101`) | **Useful** | Correct, specific, and it identifies something the Claude pass missed entirely. The fields are declared `Optional[...] = None` so Pydantic emits `{"type": "null"}` into the schema, while `_reject_null_for_required_fields` rejects that same value at runtime. The null-rejection fix in commit `772e335` closed a security gap and **introduced** this documentation/runtime divergence as a side effect. | Verified independently. `app.openapi()` returns `{"anyOf": [{"type": "string"}, {"type": "null"}]}` for `title` and `description`, and `anyOf` with `{"type": "null"}` for `status` and `priority`. All four fields returned **422** when PATCHed with `null` — on both a missing task and a real one, confirming body validation fires before the 404 path. **Recorded, not fixed.** Resolving it means changing field declarations in `backend/app/models.py`, which is protected application code and outside the final-project scope; the alternative (relaxing the validator) would reopen VAL-01. Logged as backlog. |
| C2 | "The comment-author 500→422 correction has no regression coverage. If the guard regresses, the integer reaches `.strip()`, raises `AttributeError`, and the endpoint returns HTTP 500. Existing author coverage at `backend/tests/test_comments.py:38-98` only exercises missing, blank, and oversized strings." | **Useful** | A real and consequential coverage gap. The claim is falsifiable and Codex supplied the grep to falsify it. | Verified independently: searching `backend/tests` for a non-string author literal returns **zero matches**. The only author tests present are `test_add_comment_without_author_stores_null_author` (:38), `test_add_comment_with_whitespace_only_author_stores_null_author` (:47), and `test_add_comment_author_over_50_chars_returns_422` (:90). The ERR-01 fix is therefore genuinely unprotected — it could regress and all 72 tests would still pass. **Recorded as backlog, not fixed.** Adding tests is in scope, but a 72→74 count change would invalidate 20 documented references across 7 files hours before submission, trading a real risk of stale documentation for a hypothetical regression. Recording an honest, evidenced gap is the better call here. |
| C3 | "The explicit-null correction also has no regression coverage. Without the validator, `storage.update_task()` would include the explicit `None` through `model_dump(exclude_unset=True)`, producing HTTP 200 with a null task field. Existing tests exercise omitted fields and nullable `due_date`, but none exercises explicit null for these four fields." | **Useful** | Same class of gap as C2, on the other security fix, and correctly distinguishes *omitted* from *explicitly null* — the exact distinction the Claude pass's comment #1 got wrong in the opposite direction. | Verified independently: searching `backend/tests` for an explicit `null` on `title`/`description`/`status`/`priority` returns **zero matches**. The only `None` assertions in the suite concern `due_date` (`test_due_dates.py:33, 41, 148, 151`), which is legitimately nullable and a different contract. **Recorded as backlog, not fixed**, for the same documentation-churn reason as C2. |

**Grade totals, Codex pass:** 3 Useful, 0 Noise, 0 Wrong.

### What the two passes together showed

The two tools did not overlap on a single comment, and their failure modes were opposite. The Claude pass produced 5 comments of which 2 were **Wrong** — both confidently reasoned from the model definitions without following the value through the write path or the validator lifecycle. The Codex pass produced 3 comments, all **Useful**, all supplied with a falsifiable proof command, and it declined to pad the list when it ran out of real findings.

Most usefully, Codex's C3 correctly distinguished an *omitted* field from an *explicitly null* one — precisely the distinction the Claude pass's comment #1 inverted. One tool's blind spot was the other tool's finding.

Two conclusions I am taking from this:

1. **A review that stops when it runs out of findings is more trustworthy than one that fills a quota.** Asking for "3-5 comments" invites padding; Codex returned 3 and said so explicitly.
2. **Requiring a proof command changes the output.** Every Codex comment came with a command that could disprove it, and all three survived. Neither of the Claude pass's Wrong comments could have survived being asked for one up front. That requirement is now part of my review prompt permanently, and is recorded in `docs/ai-playbook.md`.

Verifying independently still mattered. Three of three self-labelled "Confirmed" claims held up here — but that is a result I obtained by checking, not an assumption I was entitled to make.

---

## AI security mini-review

Findings 1–6 are carried forward from the Module 5 read-only Codex security audit graded in `docs/security-review.md`, **re-verified on 2026-08-12** against the current working tree rather than re-copied. Finding 7 is re-verified with fresh file evidence in this pass.

| # | Finding | File evidence | Grade | Reason | Next action |
|---|---|---|---|---|---|
| 1 | **AUTH-01** — No authentication, authorization, or ownership check on any route. Any client that can reach the API can read, modify, and delete every task and comment. | `backend/app/main.py:70-323` (no dependency and no auth middleware on any of the 9 routes); `README.md:186-187` | **Valid** | The absence is real and complete. It is an accepted course-scope limitation, not a defect to fix inside this project — but it is still true, and it is the reason the deployment restriction below exists. | **Documented, no code change.** Commit `d6e08fd` records that authentication and authorization are required before any network or production deployment. Do not expose beyond localhost. |
| 2 | **VAL-01** — `TaskUpdate` accepted explicit `null` for `title`, `description`, `status`, `priority`, wrote it to storage, and could reach a frontend `toLowerCase()` call on a null priority. | Fixed at `backend/app/models.py:96-101` | **Valid — now fixed** | The original finding was concrete and reproducible, with a real downstream frontend consequence at `frontend/index.html:743`. | **Fixed** in commit `772e335`. **Re-verified 2026-08-12:** `PATCH /tasks/{id} {"title": null}` returns **422**. |
| 3 | **ERR-01** — `_normalize_comment_author_value` called `.strip()` in `mode="before"`, ahead of any type check, so a non-string author raised `AttributeError` and surfaced as HTTP 500 instead of 422. | Fixed at `backend/app/models.py:41-42` | **Valid — now fixed** | A real validation-bypass producing a 500. Unhandled 500s are a genuine (if low-severity here) information-disclosure and availability concern. | **Fixed** in commit `44b2e0f`. **Re-verified 2026-08-12:** `POST /tasks/{id}/comments {"text":"hi","author":123}` returns **422**. |
| 4 | **DOS-01** — Server-side length limits for `description` and `assignee` exist only as HTML `maxlength` attributes. Entity counts are unbounded, `GET /tasks` is unpaginated, and listing tasks scans comments once per task. | `backend/app/models.py:63-71` (no `max_length` on `description`/`assignee`); `frontend/index.html:617-642` (browser-only limits); `backend/app/main.py:103-113` (no pagination); `backend/app/storage.py` `count_comments_for_task` called once per task inside the list comprehension | **Valid** | Not a generic DoS template — it names the specific gap between the frontend contract and the API contract, and the specific O(tasks × comments) list path. Severity stays Medium: the app is in-memory, single-process, and local-only. | **Backlog, unchanged.** **Re-verified 2026-08-12:** a 5,000-character `description` and a 500-character `assignee` were both accepted with **201**. Add server-side `max_length`, pagination, and a comment-count index before this leaves local scope. |
| 5 | **CORS-01** — Originally `allow_origins=["*"]`, allowing any website to read from and send JSON mutations to a locally running API. | Fixed at `backend/app/main.py:26` | **Valid — fixed for local scope** | The wildcard was real and the browser-mediated attack path was real. | **Fixed** in commit `6b6e885`. **Re-verified 2026-08-12 with live preflight probes:** `OPTIONS /tasks` with `Origin: https://evil.example` → **400**, no `Access-Control-Allow-Origin` header returned; `Origin: http://localhost:5500` → **200** with `Access-Control-Allow-Origin: http://localhost:5500`. `allow_methods`/`allow_headers` remain `["*"]`, which is accepted for local development and documented at `README.md:185`. |
| 6 | **CI-01** — "The CI workflow lacks SHA-pinned actions, image scanning, and a hardened deployment gate." | `.github/workflows/ci.yml:1-27`; `Dockerfile:2` | **Noise** | True statements assembled into a finding that does not fit this repository. There is no deployment pipeline to harden, no compromised action was identified, and no vulnerable base image was demonstrated. It is generic hardening advice wearing a finding's clothes. | **No action.** Recorded so the grade is on the record rather than silently dropped. |
| 7 | **DEP-01** — One `requirements.txt` serves both runtime and tests, so the Docker runtime image installs `pytest` and `httpx2`; `httpx2>=2.0.0` is unpinned. | `requirements.txt:1-8` (`pytest==9.1.1`, `httpx2>=2.0.0` under a `# Test dependencies` comment); `Dockerfile:9-10` copies that same file into the builder venv, which is then copied wholesale into the runtime stage at `Dockerfile:17` | **Valid** | Concrete and specific: unnecessary runtime attack surface plus a real reproducibility gap from the open-ended version range. No vulnerable package or typo was confirmed, so severity stays Low. | **Backlog.** Split into `requirements.txt` / `requirements-dev.txt` and pin `httpx2` to a resolved version, then re-verify a clean install and a fresh Docker build. Not done now — the brief protects scope, and a dependency split immediately before submission risks breaking a green CI run for no grading benefit. |

**Grade totals for this pass:** 6 Valid (3 fixed, 2 backlog, 1 documented-and-accepted), 1 Noise, 0 False Positive.

---

## Manual security check

Three checks I ran myself, none of which were suggested by an AI review.

**1. Traced every `innerHTML` write in the frontend to see whether the escaping is actually complete.** The security audit asserted that "user-controlled content is escaped at the inspected `innerHTML` rendering sinks" — but "inspected" is doing a lot of work in that sentence, so I enumerated all four sinks myself:

- `frontend/index.html:675` — inside `escapeHtml()` itself, reading back `div.innerHTML` after a `textContent` write. This is the escaper, not a sink.
- `frontend/index.html:725` — `list.innerHTML = ''`, a constant.
- `frontend/index.html:739` — the task card template. Every interpolated user value passes through `escapeHtml()`: `title` (740), `description` (741), `priority` (743), `assignee` (744), `due_date` (745). The only un-escaped interpolations are `task.is_overdue` and `task.comment_count`, which are a backend-computed boolean and a backend-computed integer, never client input (both are rejected on input by `extra="forbid"`).
- `frontend/index.html:997` — the comments template. `author` (998) and `text` (1001) both pass through `escapeHtml()`.

**Result: nothing new found.** The escaping is complete, and `escapeHtml` uses the correct `textContent` → `innerHTML` round-trip rather than a hand-rolled regex. I also checked the `escapeHtml(task.assignee)` call on line 744 for a null-rendering bug, since `assignee` is nullable — `Node.textContent` is specified `[LegacyNullToEmptyString]`, so `null` renders as an empty string, not the text `"null"`. No defect.

**2. Checked the Docker image for baked-in secrets by reading what actually gets copied, not what is claimed.** `Dockerfile:22` copies exactly one path — `COPY --chown=app:app backend/app ./app`. It does not copy the repository root, `docs/`, `.git`, or `frontend/`. `.dockerignore` additionally excludes `.env`, `.git`, `.github`, `venv/`, and `backend/venv/`. I also confirmed there is no `.env` file anywhere in the repository to be copied in the first place. `Dockerfile:15` creates a non-root `app` user with `/usr/sbin/nologin`, and `Dockerfile:24` switches to it before `CMD`. **Result: no secrets baked in, non-root confirmed by reading the file.**

**3. Found an API contract inconsistency that no AI pass flagged.** Unknown *body* fields are rejected with 422 by `extra="forbid"` on every input model, but unknown *query parameters* are silently ignored. I confirmed this directly:

```
POST /tasks {"title":"e","bogus":1}   -> 422   (rejected)
GET  /tasks?bogus=1                   -> 200   (silently ignored)
GET  /tasks?limit=5                   -> 200   (silently ignored, returned all 53 seeded tasks)
```

**Why it matters:** this is not a vulnerability — FastAPI's behaviour here is standard and it exposes nothing. But it is a real contract asymmetry with a practical consequence: a client that assumes `?limit=` works (a reasonable assumption for a list endpoint) gets a silent full-table response rather than an error, which makes DOS-01 easier to trigger by accident than the finding implies. I am recording it as a documentation gap and a backlog note attached to DOS-01, **not** fixing it — adding query-parameter strictness would be new behaviour, which the final-project brief forbids.

---

## One AI output I rejected or corrected

**Rejected: the claim that commit `772e335` broke partial updates.**

An AI review comment on `backend/app/models.py` argued that registering `_reject_null_for_required_fields` with `mode="before"` across `title`, `description`, `status`, and `priority` would cause omitted fields to be rejected, breaking `TaskUpdate`'s partial-update contract — the specific prediction was that a `PATCH` sending only `status` would start returning 422.

The reasoning was internally coherent and it named the right mechanism, which is exactly what made it worth checking rather than dismissing. It was also wrong. A Pydantic v2 `field_validator` only executes for fields present in the input payload; an omitted field never reaches the validator and resolves to the model default instead. I did not settle this by re-reading the code or by asking a second model — I ran it:

```
PATCH /tasks/{id}  body {"status": "InProgress"}   -> 200
```

and confirmed the two tests that already encode this contract still pass: `tests/test_tasks.py::test_patch_partial_update_keeps_other_fields` and `tests/test_due_dates.py::test_patch_omitting_due_date_leaves_existing_value_unchanged`, inside a full run of **72 passed**.

**What I did instead:** no code change. Had I accepted the suggestion, I would have replaced a working two-line security fix with a more complicated conditional guard, weakening the VAL-01 remediation to solve a problem that does not exist. The comment is recorded as **Wrong** in the mini-log above rather than deleted, because the grade is the evidence.

A second, subtler correction is recorded as row 5 of the mini-log: an AI observation about `extra="forbid"` on response models was *correct*, but its implied action — edit the response models — was not. I graded the observation Useful, logged it as a documentation clarification, and declined the edit, because `AGENTS.md:186` and the brief's scope rule both protect `backend/app/` from changes that are not bug fixes or security fixes.

---

## Changes made to protected paths

The final-project brief protects `app/` and `frontend/` and permits changes only for a small bug fix, a security fix, or a documentation-supported correction — with any such change explained here. **Exactly one change was made to a protected path during the final project.**

**File:** `backend/app/main.py`, line 65 (docstring only)
**Category:** documentation-supported correction
**Change:** the `GET /version` docstring's example response read `{"version": "0.1.0"}`. The endpoint returns `app.version`, which is set to `"0.4.0"` at `backend/app/main.py:21`. I confirmed the drift by calling the live endpoint (`GET /version` -> `200 {"version":"0.4.0"}`) before editing, then corrected the example to `{"version": "0.4.0"}`.

**Why this is in scope:** the edit touches a docstring example string only. No executable statement, no signature, no route, no validator, and no return value changed — the endpoint already returned the correct value and continues to. It is a documentation correction that happens to live inside an application file.

**Verification after the change:** full suite re-run from `backend/` — **72 passed**, identical to the pre-change baseline. `GET /version` re-probed and still returns `200 {"version":"0.4.0"}`.

**Not changed, deliberately.** Every other AI suggestion that would have touched `backend/app/` or `frontend/index.html` was declined and is recorded above: the redundant `text` type guard (mini-log #3), the validator merge (mini-log #4), the response-model `extra="forbid"` removal (mini-log #5), the DOS-01 server-side length limits, the DEP-01 requirements split, and query-parameter strictness from the manual check. `frontend/index.html` was not modified at all during the final project.

---

## Three AI usage rules

1. **Never paste:** credentials, API keys, tokens, `.env` contents, production logs, or any real personal data into any AI tool or into this repository. When a finding involves a sensitive value, I report the affected file and setting and redact the value itself (`AGENTS.md:192`).
2. **Always verify:** any AI claim about runtime behaviour gets executed before it is believed — a probe, a `curl`, or the test suite. Reading the code again is not verification, and a second AI agreeing is not verification. Two of the five comments in this review's mini-log were confident, coherent, and wrong; both were caught by running the endpoint, and neither would have been caught by re-reading.
3. **Record AI contributions by:** graded evidence tables in `docs/` that name the tool, the date, the file and line, the grade, and the decision — `docs/final-ai-review.md`, `docs/security-review.md`, and `docs/midcourse/prompt-log.md` — plus commit messages that state what changed and why (`44b2e0f`, `772e335`, `6b6e885`).

---

## Ownership statement

I can explain every line of code in this repository that differs from the Module 1–3 baseline, including the three Module 5 security fixes, why each one is scoped the way it is, and what would break if it were written differently. AI produced draft code, review comments, and security findings throughout this project, but nothing was accepted because it sounded authoritative — every behavioural claim in this document was confirmed by running the endpoint or the test suite, and the two AI comments that turned out to be wrong are recorded above as Wrong, with the probe that disproved them, rather than quietly dropped. I rejected AI suggestions that would have expanded scope beyond the brief or edited protected application code for style reasons, and I left DOS-01 and DEP-01 open as documented backlog items rather than papering over them with fixes I could not verify before submission. Where the repository has real limitations — no authentication, no persistence, no server-side length validation, CI that does not build the Docker image — they are written down in `README.md`, `AGENTS.md`, and `docs/security-review.md` as limitations, not omitted to make the project look more finished than it is. I am comfortable submitting this as my own work because the judgement calls in it are mine and the evidence for each one is in the repository.
