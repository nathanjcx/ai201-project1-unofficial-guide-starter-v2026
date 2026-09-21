# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, recorded in unit 1
before running the five test questions or tuning retrieval in Milestone 4.
The starter's chunk statistics and one baseline email answer were already seen.
Criteria 1–3 come from the assignment. Codex drafted the explanations and
criteria 4–5; this assistance is also recorded in the README.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
My questions cover different topics, like email, textbooks, and commuting, so
the system needs to find the right thread for each one. I chose 4 out of 5
because it might find a related chunk that misses the answer once, but missing
two would be too many for a small set of basic questions.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
The threads contain advice from different students, so I want to be able to
open the original document and check an answer. I chose every answer because
the system already gets the source filenames, and leaving one out would make
that answer harder to verify.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
These documents are about student life, so the system should usually stop
questions about unrelated subjects before asking the model to answer. I chose
4 out of 5 to allow one confusing match, but accepting two unrelated questions
would make the gate unreliable; the cutoff will be chosen from distances later.

---

## 4. Chunks keep the discussion context

All five chunks printed by `python app.py --corpus advice_threads chunks -n 5`
must include their original thread title and at least one complete reply,
with no reply cut off at either boundary.

**Why this target:**
Replies such as "Varies enormously" or "Both true" depend on the surrounding
discussion, and the starter even produced a 2-character fragment. I chose all
five because a retrieved fragment can lose the meaning of the advice even if
it contains the right keywords.

---

## 5. The cited documents support the advice

For at least 4 of my 5 test questions, the system must give a non-refusal
answer whose factual claims are all supported by the document or documents
it explicitly cites. A refusal, an unsupported claim, or a claim with no
cited document supporting it counts as a failed question.

**Why this target:**
Naming a file is not enough if that file does not actually support the answer,
especially when different students give conflicting advice. I chose 4 out of
5 to allow one grounding mistake while still expecting most answers to be
checkable against their sources.

### How these will be checked in unit 2

- Use the five entries in `questions.py::QUESTIONS`, with top-k from `config.py`.
  For criterion 1, read the retrieved text and check for the answer, not just a
  matching word. The `expects` phrases are helpful hints rather than proof.
- For criterion 2, count source filenames in each generated answer; the CLI's
  separate "Sources retrieved" list does not count as an answer citation.
  Gate refusals are assessed under criterion 3.
- For criterion 3, run all five `OUT_OF_SCOPE` questions through the gate and
  check that at least four return the refusal without calling the model.
- For criterion 4, compare the five printed chunks with their source files.
- For criterion 5, open each document named in the answer and find support for
  every factual claim, including numbers and timing. The target must hold in
  each of the three evaluation runs required in unit 2.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
