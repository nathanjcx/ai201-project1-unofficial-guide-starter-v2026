# The Unofficial Guide

Nathan Cheng — `advice_threads`

# Unit 1

## What This Does

This is a command-line question-answering tool for the 23 student discussions
in `advice_threads`. It answers questions about things like professor emails,
textbooks, commuting, bikes, and group projects. It searches the documents and
uses a model to write a short answer with the source filename. When the search
results are too far from the question, it returns "I don't have enough
information about that" before calling the model.

For a fresh clone, use Python 3.11–3.13 and install the starter dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Set `GEMINI_API_KEY` in `.env`, following `.env.example`, then run:

```bash
python test.py
python app.py index
python app.py ask "How much does renting a locker in the commuter lounge cost per year?"
```

`advice_threads` is the default in `config.py`. An `AI201_CORPUS` value in
`.env` overrides it; use `--corpus advice_threads` to choose it explicitly.
The key, downloaded packages, model-response cache, and vector store stay out
of Git. A fresh clone needs its own key and a new `index` run. More commands
are in [RUNNING.md](RUNNING.md).

## Chunking Strategy

**Chunk size:** 800 characters as a soft limit, keeping whole threads together
when they fit.
**Overlap:** 0 characters of reply text. For a longer thread, repeat its title
in each chunk and split only between complete replies.

Plan recorded before implementing the new chunker: the 23 cleaned advice
threads are 317–793 characters long, so each complete discussion fits within
800 characters. Keeping the replies together matters because some begin with
"Both true" or "Varies enormously" and need their question or earlier replies.
If a future thread is longer, group complete replies up to the target; allow a
single long reply to exceed it rather than cutting a sentence. Other document
formats will use complete paragraphs as their boundaries.

The starter used 800-character windows with 120-character overlap and made
26 chunks, averaging 487 characters. The shortest was 2 characters (`t.` from
`thread_meal_plan_tier.txt#1`); the longest was 793. It generated an unnecessary
overlap tail even when a thread already fit in one chunk. The class activity
number, recorded before changing the chunker, was **26**.

The implemented `chunker.py::split_documents` produces **23 chunks**, averaging
**543 characters**, with a **317-character minimum** and **793-character maximum**.
Every thread in this corpus stays in one chunk. This removes the redundant
tails while retaining disagreements between replies. The tradeoff is that
a whole thread can include several pieces of advice, so retrieval may still
bring back material that is only partly relevant. For future longer threads,
a reply may refer to a previous chunk; repeating the title does not solve
every dependency between replies.

`ingest.py::clean_text` already normalizes line endings, repeated whitespace,
and extra blank lines. The supplied threads have no website navigation or
ads to remove; thread titles, reply labels, and votes are retained.


## Sample Chunks

Printed with `python app.py --corpus advice_threads chunks -n 5`.

**Chunk 1** — source: `thread_bike_commute.txt#0` — produced by: `chunker.py::split_documents`

```text
THREAD: Is a bike worth it for a 20 minute walk commute?

--- reply 1 (14 votes) ---
Yeah. Cuts an 18 minute walk to about 6. The thing nobody mentions is storage — covered bike parking exists at three buildings and is full by 9am at all three.

--- reply 2 (9 votes) ---
Counterpoint, I sold mine. Between November and March the paths are either icy or salted and salt destroys a drivetrain in one season.

--- reply 3 (22 votes) ---
Both true. I keep a cheap bike for September to November and walk the rest of the year. Total cost was about $120 for the bike and I don't care what happens to it.

--- reply 4 (5 votes) ---
If you do get one, the campus does free registration and it's the only reason I got mine back after it was taken.
```

**Chunk 2** — source: `thread_first_gen.txt#0` — produced by: `chunker.py::split_documents`

```text
THREAD: Anything specific for first-generation students?

--- reply 1 (33 votes) ---
The advising office has a specific programme and it is genuinely good, but it is opt-in and badly publicised. Ask for it by name.

--- reply 2 (41 votes) ---
The thing I'd say: the unwritten rules are the hard part, not the coursework. Ask about the unwritten rules explicitly. People are happy to explain them and nobody volunteers them.

--- reply 3 (16 votes) ---
Emergency fund for textbooks and travel exists and is not means-tested beyond a short form.
```

**Chunk 3** — source: `thread_laptop_specs.txt#0` — produced by: `chunker.py::split_documents`

```text
THREAD: How much laptop do I actually need for CS courses?

--- reply 1 (31 votes) ---
Less than the recommended spec page says. 16GB of RAM is the one number worth paying for; everything else you'll never notice.

--- reply 2 (18 votes) ---
Adding: the lab machines exist and are better than anything you'll buy. For the heavy assignments people just use those.

--- reply 3 (12 votes) ---
I did two years on an 8GB machine and it was fine until the last project, at which point it very much wasn't. 16 is the answer.
```

**Chunk 4** — source: `thread_office_hours_etiquette.txt#0` — produced by: `chunker.py::split_documents`

```text
THREAD: Is it weird to go to office hours with no specific question?

--- reply 1 (44 votes) ---
No, and this is the single most common thing first years get wrong. 'I'm following the lectures but I don't feel like I understand the shape of it' is a completely normal thing to say.

--- reply 2 (29 votes) ---
They're usually empty. You are doing the instructor a favour by turning up.

--- reply 3 (18 votes) ---
If it helps, treat it as a standing appointment. Go every week for a month and it stops feeling like a thing.
```

**Chunk 5** — source: `thread_professor_email.txt#0` — produced by: `chunker.py::split_documents`

```text
THREAD: Do professors actually answer email?

--- reply 1 (21 votes) ---
Varies enormously. General rule I've found: if the syllabus states a response window, it's honoured. If it doesn't, assume 48 hours and don't panic before then.

--- reply 2 (33 votes) ---
Office hours are dramatically more effective than email for anything that takes more than two sentences to answer. They're also usually empty.

--- reply 3 (15 votes) ---
Empty office hours is the biggest unused resource here and I say that having wasted a year not going.
```

All five include their thread title and complete replies. On their own,
they can answer questions about biking in winter, first-generation support,
laptop RAM, visiting office hours, and professor email response times.

## Sample Answer

**Question:** How much does renting a locker in the commuter lounge cost per year?

**Answer:**

```text
According to a reply in the commuting thread, renting a locker in the commuter lounge costs $20 a year.

Source: thread_commuting.txt
```

This is the complete answer returned by `app.py::ask_pipeline` during the
final development check. Its best retrieval distance was
**0.602432**. The source containing the $20 price ranked
third; the top result was about bikes and did not answer the locker question.

**Top-k:** 5. The locker result shows why using only the first result would
miss useful information. Keeping five leaves room for another relevant result,
but also gives the model loosely related text, so the grounding instruction
must tell it to use only sources that actually support the answer.

**My relevance cutoff:** 0.7, using cosine distance. Smaller means closer,
and the gate passes only when the best distance is strictly below the cutoff.

| Question | In corpus? | Best distance |
|---|---|---|
| How long should I wait for a professor to reply if no given response window? | Yes | 0.410175 |
| Where can I check the current textbook edition's problem numbering for free? | Yes | 0.350329 |
| How much does renting a locker in the commuter lounge cost per year? | Yes | 0.602432 |
| What damages a bike's drivetrain during winter? | Yes | 0.520547 |
| When should I raise a group project problem with the instructor to get individual grades adjusted? | Yes | 0.395847 |
| What is the capital of Mongolia? | No | 0.947917 |
| How do I change the oil in a diesel engine? | No | 0.929855 |
| Who won the 1994 World Cup? | No | 0.951709 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.828034 |
| How do I write a for loop in Rust? | No | 0.871231 |

The in-corpus best distances ranged from **0.350329 to 0.602432**. The
out-of-corpus best distances ranged from **0.828034 to 0.951709**. The 0.7
cutoff sits in that gap and leaves some room on both sides. The original 0.6
cutoff would have refused the locker question at 0.602432 even though its
answer was in the top five. A cutoff above 0.828034 would start admitting an
unrelated question from this set.

For example, asking "What is the capital of Mongolia?" produced:

```text
I don't have enough information about that.
```

Its best distance was 0.947917. All five out-of-corpus questions were refused,
with **zero model calls** for those questions. This is checked before
`generate.py::answer_from_chunks` runs.

The grounding prompt tells the model to use only the supplied text, preserve
qualifications and disagreements, and finish with an exact source filename.
An initial check still produced an unsupported "by week 10 at the latest"
deadline for group projects. The thread only used week 10 as an example of
arriving without documentation. Codex added instructions against turning
examples into deadlines and reran all five questions with caching disabled;
the revised answer kept the before-deadline advice and the documentation
example separate. The original output remains in the evidence folder.

**Development checks:**

- `python test.py`: 10 passed, 0 failed.
- `python -m unittest discover -s tests -v`: 6 chunker tests passed, including
  content preservation, long threads, oversized replies, and empty input.
- The bundled pipeline smoke test passed using stand-in models and a separate
  temporary vector store. It checks the pipeline, not retrieval quality.
- One final pass using real embeddings and real model calls retrieved an
  answer-containing thread for all five questions. All five generated answers
  cited their supporting document; Codex checked the factual claims against
  the source text. All five unrelated questions stopped at the gate.

These are unit 1 development observations. The three-run unit 2 evaluation
has not been performed, and its template is left below for that work. Five
covered and five clearly unrelated questions are a small tuning set; new
questions, especially unsupported questions about student life, may behave
differently. A close retrieval score does not prove an answer is in the text,
and a citation does not by itself prove the model used that text correctly.

The measurements, full retrieved text for the first three questions, prompts,
original and final answers, and test logs are in [results/](results/).
`results/unit1-answers.json` contains the final model outputs;
`results/unit1-answers-initial.json` preserves the earlier grounding mistake.

## How I Used AI

**1. Setup and test questions.** I had codex up on the right and vscode on the left and followed along with explanations behind the theory of the assignment.
I also asked for five simple questions. It explained why a reply needs its thread
title and suggested questions with expected answer phrases. I ran the setup
check, chose `advice_threads`, indexed it, asked the first email question,
edited `questions.py`, and made the first commit. Before testing the five
questions, Codex made the textbook question more specific and changed
`before deadline` to `before the deadline` to match the source wording.

**2. Completing the implementation and checking answers.** I later asked
Codex to finish the remaining project. It drafted the criteria explanations
and criteria 4–5, wrote the custom chunker, measured retrieval distances,
selected the cutoff, and completed this README using real outputs. During
its checks, the model added an unsupported week-10 deadline; Codex tightened
the grounding prompt and verified the revised outputs. The code and prompt
changes in this stage were made by Codex, and the initial failed answer is
saved alongside the final answers.

This project includes substantial AI assistance. Criteria 1–3 are supplied by
the assignment; the other two and their explanations are AI-assisted drafts,
not independently student-authored criteria. The commit history records the
actual order of work, including the criteria commit before retrieval tuning.
No stretch features are claimed.

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
