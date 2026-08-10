# Security Review Grading Worksheet

Date: 2026-08-10
Scope: Module 5 review of the seven findings from the read-only Task Tracker security audit.

These grades were confirmed by the student. The reasons and evidence below describe the pre-remediation audit state; the current disposition is recorded under Resolution status. A finding marked Valid may be an intentional course-scope limitation rather than a defect that must be fixed now.

## Original grading

| Finding ID | Grade | Reason | Evidence needed or evidence used | Student decision |
|---|---|---|---|---|
| AUTH-01 | Valid | The API has no authentication, authorization, or ownership checks. This is explicitly documented and acceptable for the learning scope, but it would allow any reachable client to read, modify, and delete all data outside that scope. | `backend/app/main.py:70-323`; `README.md:179-185`; `Dockerfile:28` | Valid (student) |
| VAL-01 | Valid | Explicit `null` values for `title`, `description`, `status`, and `priority` are accepted by `TaskUpdate` and copied into stored tasks even though the response schema treats them as required. This can violate the API contract; null priority also reaches a frontend `toLowerCase()` call. | `backend/app/models.py:84-92`; `backend/app/main.py:202-205`; `backend/app/storage.py:114-125`; `frontend/index.html:743`. Isolated TestClient probes returned 200 and null values for all four fields. | Valid (student) |
| DOS-01 | Valid | This is repo-specific rather than a generic denial-of-service claim: description and assignee limits exist only in HTML, entity counts are unlimited, responses are unpaginated, and listing tasks scans every comment once per task. Its practical importance is limited in the in-memory course application, so the existing Medium rating should not be increased. | `backend/app/models.py:61-69`; `frontend/index.html:617-642`; `backend/app/main.py:103-113`; `backend/app/storage.py:218-227`. An isolated probe accepted a 2,001-character description and 51-character assignee with HTTP 201. | Valid (student) |
| ERR-01 | Valid | The comment-author pre-validator calls `.strip()` before checking the raw input type. Non-string JSON values therefore escape normal validation and produce HTTP 500 rather than 422. | `backend/app/models.py:38-46` and `backend/app/models.py:134-137`. Isolated model probes raised `AttributeError` for integer, object, and array values; the endpoint probe returned HTTP 500 with `Internal Server Error`. | Valid (student) |
| CORS-01 | Valid | Wildcard origins, methods, and headers allow arbitrary websites to read from and send JSON mutations to a locally running API. The configuration is documented as local-only, but that does not make the cross-origin behavior false; it remains a limitation that matters if the service is reachable. | `backend/app/main.py:24-29`; `frontend/index.html:665-690`; `README.md:181-184` | Valid (student) |
| DEP-01 | Valid | The same requirements file supplies both runtime and test dependencies to the container, and `httpx2>=2.0.0` is open-ended. This is a concrete reproducibility and runtime-surface issue, but no vulnerable package or typo was confirmed, so it should remain Low priority. | `requirements.txt:1-8`; `Dockerfile:9-18`. The installed Starlette warning specifically recommends `httpx2`, so its name is not graded as a confirmed typo. | Valid (student) |
| CI-01 | Noise | The observations are true, but the combined claim is primarily generic hardening advice: the course CI is intentionally a pytest workflow, no production deployment pipeline exists, and the audit demonstrated no compromised action, vulnerable base image, or Docker build failure. It is reasonable engineering backlog material, but weak as a standalone security finding in this scope. | `.github/workflows/ci.yml:1-27`; `Dockerfile:2`; `README.md:130-139`. A live advisory check and Docker build were not performed. | Noise |

## Resolution status

| Finding ID | Status | Evidence or next action |
|---|---|---|
| AUTH-01 | Documented | Commit `d6e08fd` states that authentication and authorization are required before network or production deployment. The course-scope limitation remains intentional. |
| VAL-01 | Fixed | Commit `772e335` rejects explicit null for task-update `title`, `description`, `status`, and `priority` with 422 while preserving omitted-field behavior. |
| DOS-01 | Backlog | Add server-side field limits, pagination/quotas, request controls, and a more efficient comment-count strategy before moving beyond the in-memory course scope. |
| ERR-01 | Fixed | Commit `44b2e0f` rejects non-string comment authors with 422 instead of returning 500. |
| CORS-01 | Fixed for local scope | Commit `6b6e885` restricts origins to `http://localhost:5500` and `http://127.0.0.1:5500`; methods and headers remain unrestricted for local development. |
| DEP-01 | Backlog | Split runtime/test requirements and lock intentionally resolved versions; verify a clean install and Docker image when implemented. |
| CI-01 | No action | Graded Noise for this course scope. |

## Audit context retained from the original review

- Strong validation already exists for task titles, enum values, unknown fields, due dates, comment text, and normal string authors.
- User-controlled task and comment content is escaped at the inspected `innerHTML` rendering sinks.
- No credentials, root `.env`, enabled debug mode, or client-visible stack trace was observed in the inspected files.
- Database injection is not applicable because storage uses module-level dictionaries.
- The Docker runtime uses a non-root user.
- Comment deletion is scoped to its parent task, and deleting a task removes its comments.

## Limits

- The initial audit was primarily static. Remediation used isolated red/green TestClient probes, and the full 72-test suite passed after the CORS-01, ERR-01, and VAL-01 changes; the Docker image was not rebuilt.
- No live dependency-advisory lookup, load test, concurrency test, or comprehensive secret scanner was run.
- Ratings assume the service could eventually be exposed beyond a trusted local machine. Within the documented course-only setup, several Valid items are deferred limitations rather than immediate remediation requirements.
