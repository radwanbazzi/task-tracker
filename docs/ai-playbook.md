# My AI Playbook

**Youssef Bazzi — AI-Assisted Coding (AUB), written after finishing the final project, 2026-08-12**

I came into this course non-technical. Every rule below is here because something in this repo taught it to me, not because it sounded responsible.

---

## When I reach for AI first

- **Test scaffolding.** Writing the 27 comment tests by hand would have taken me a week. AI got the structure right and I checked the assertions. This is the highest-leverage use I found all course.
- **Config files I've never written before.** `ci.yml` and the multi-stage `Dockerfile` — I had no mental model for either. AI gave me a working draft fast, and *then* I learned what each line did by breaking it on purpose (the intentional red CI run, commit `066c8a4`, reverted at `8544659`).
- **Read-only review passes.** Pointing an agent at a diff or at `backend/app/` and asking "what's wrong here" surfaces things I'd never spot. The value is in the volume of candidates, not in the accuracy — I graded 5 code comments this pass and only 1 was Useful.
- **Explaining code back to me.** "Why does `mode='before'` matter here" is the question that actually moved my understanding forward.
- **Docs drafting.** Turning things I already verified into readable prose.

## When I do not reach for AI first

- **Anything touching `backend/app/` or `frontend/index.html`.** These are the only files that make the app work. I've fixed 3 real security bugs in them and I want to keep understanding all of them.
- **When I can't yet judge the answer.** If I don't know enough to tell a good answer from a confident wrong one, generating code is just borrowing a problem. Two of five AI comments in my final review were flatly wrong and both *sounded* right.
- **Deciding scope.** AI kept offering me improvements — merge these validators, add a guard here, pin these actions. Nearly all of it was outside what I was asked to do. Scope is a judgement call, not a code suggestion.
- **Architecture decisions.** The in-memory-storage decision in `docs/technical-note.md` is mine. AI can list trade-offs; it can't decide what this project is for.
- **When I'm tired and just want it to be done.** That's exactly when I stop checking, and it's the failure mode I actually have.

## My non-negotiables

- No credentials, tokens, `.env` contents, or real personal data into any AI tool or into the repo — ever, including "just to debug it."
- **Nothing about runtime behaviour is true until I've run it.** Not when the code looks right. Not when a second model agrees.
- I don't submit a line I can't explain out loud.
- Findings get graded and written down — Valid / False Positive / Noise, Useful / Noise / Wrong — with the file, the line, and the decision. A dropped finding is a hidden one.
- Limitations get documented as limitations. No auth, no persistence, no server-side length caps — all of it is in the README, because hiding it would make the project look more finished than it is.

## My review rules

1. **Read the diff before the explanation.** `git show <commit>` first, AI's summary second. Otherwise I'm grading the summary.
2. **Probe, don't re-read.** Every behavioural claim gets a `TestClient` call or a `curl`. Re-reading the same code just reproduces the same misunderstanding.
3. **Narrow test, then full suite.** The specific test that covers the change, then `pytest -v` — and I record the actual number (72 passed), not "tests pass."
4. **Grade every comment, including the bad ones.** The Wrong grades are the most useful thing in `docs/final-ai-review.md`, because they show where the judgement happened.
5. **Separate the observation from the action.** An AI comment can be *correct* and its suggested fix still wrong for this repo — that happened with the `extra="forbid"` note on response models. I logged the observation and declined the edit.
6. **Make the review supply its own disproof.** I ask every AI review for the exact command that would prove each comment wrong, and for a Confirmed-vs-Inference label. Running two tools over the same diff showed why: the pass that had to supply proof commands scored 3 Useful / 0 Wrong, while the pass that did not scored 1 Useful / 2 Wrong. Same code, same diff.
7. **Ask for "as many as you find," not "3-5."** A quota invites padding. The review that returned 3 comments and said it had nothing more was the more trustworthy one.
8. **Check docs against the running app, not against other docs.** That's how I caught the stale `allow_origins=["*"]` claim in `docs/technical-note.md` and the `/version` docstring still showing `0.1.0` when the API returns `0.4.0`.

## What I am still figuring out

- How much AI-written code I can carry before I quietly stop understanding my own project. I haven't hit that line yet, but I don't know where it is.
- Whether one strong agent with good guardrails beats switching tools, or whether the disagreement between two tools is itself the signal.
- When a documented backlog item (DOS-01, DEP-01) stops being honest scoping and starts being an excuse. Right now the answer is "when the app leaves localhost," but that's a boundary I set, not one I've tested.
- How any of this changes on a team, where the person reviewing my AI-assisted diff isn't me.

---

## Decision Card

| Situation | What I do |
|---|---|
| **New feature** | Write the user story and acceptance criteria myself first. AI drafts tests, then implementation. Nothing merges until the narrow tests and the full suite are green. |
| **Code review** | AI reviews the diff for candidates; I grade every comment Useful / Noise / Wrong with a reason and verify anything behavioural by running it. Correct observation ≠ correct action. |
| **Debugging** | I reproduce the failure myself before asking. AI proposes a cause; a probe confirms or kills it. No fix goes in on a theory. |
| **Infrastructure** | Draft with AI, then read every line and check for shortcuts — `continue-on-error`, `\|\| true`, skipped test steps, unpinned versions. Build and run it locally before I believe it. |
| **Never paste** | Credentials, tokens, `.env` contents, production logs, real personal or customer data. |
| **One rule** | **If I can't explain it, I don't ship it.** |
