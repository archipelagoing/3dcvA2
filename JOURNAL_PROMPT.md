# Learning Journal Prompt

Copy the prompt below into a conversation while working in the target repository.
It creates or updates `JOURNAL.md` using the project's actual files and evidence.

```text
Create or update a learning journal for this repository in JOURNAL.md.

Purpose

The journal should explain how understanding developed over time. Reading its
entries from oldest to newest should reveal what was known at each stage, what
was investigated, what the evidence showed, and how that informed the next step.
Keep TODO.md, or the existing project checklist, as the source of remaining work.
The journal explains learning and decisions rather than duplicating the backlog.

Before writing

1. Read the current request, applicable repository instructions, the project
   checklist, README, and relevant source files or specifications.
2. Check whether a journal already exists. Preserve its entries and use its
   established filename unless there is a clear reason to rename it. Keep one
   authoritative learning journal.
3. Identify what is supported by direct inspection, recorded results, or explicit
   user reports. Do not infer that planned work has happened.
4. Do not execute the backlog merely to populate the journal. Journal setup alone
   authorizes documentation work, not implementation or external actions.

Organization

- Start with a brief project purpose and a note explaining how to read the journal.
- Order entries oldest to newest, with consecutive numbers and descriptive titles.
- Create an entry for a meaningful investigation, experiment, discovery, decision,
  or completed stage. Do not create an entry for every small edit.
- Keep each entry understandable without requiring the conversation history.
- Link to relevant repository files, output artifacts, and earlier entries using
  portable relative links where possible. Do not include machine-specific paths.
- For a long journal, add a short linked index in chronological order.

Use this entry structure, adapting the length to the significance of the work:

## 01 — Descriptive stage title
Date: YYYY-MM-DD
Related checklist: Section title or relative link, if one exists

### Starting point
What was known before this stage, what remained uncertain, and the question this
stage aimed to answer. Avoid explaining the starting point using later knowledge.

### Work performed
What was inspected, implemented, or tried. Record relevant commands, input data,
parameters, and environment details when needed to reproduce the investigation.
Keep the account focused on actions that explain the result.

### Evidence
What was actually observed or measured. Link to code, outputs, or recorded results.
Distinguish direct observations, user-reported results, assumptions, and inferences.
Record failed attempts when they explain a discovery or decision. Never invent
commands, test outcomes, measurements, or completion evidence.

### What we learned
State the concrete conclusion supported by the evidence and explain why it matters.
Describe how understanding changed, including any expectation that proved wrong.
If evidence is insufficient, say what remains unproven instead of forcing a lesson.

### Remaining uncertainty
What this stage did not establish, what could not be checked, and any limitation
that affects the interpretation of the result.

### Decision and next step
Explain the decision justified by this stage and the next question or action.
Reference the checklist rather than copying its full task list. A proposed action
is not a completed action or authorization to perform unrelated work.

Initial setup

- If only repository inspection has occurred, create one initial entry documenting
  that inspection, the available materials, and the known gaps. Explicitly state
  that implementation and runtime behavior have not been verified.
- If historical work is documented, summarize it only to the extent supported by
  records. Label reconstructed entries as retrospective and cite their sources.
- Use the actual event date when known. Otherwise record the date of review and
  state that the original event date is unknown. Do not invent a chronology.
- Do not prewrite future entries as though those stages have happened. Suggested
  future stages belong in the checklist, not among completed journal entries.

Ongoing maintenance

- After authorized work produces meaningful evidence or changes understanding,
  append a journal entry and update the relevant checklist separately.
- Preserve earlier conclusions as historical records. If later evidence overturns
  one, add a new entry explaining the correction and link both entries. A short,
  clearly labeled correction note may be added to the earlier entry so readers
  can find the current conclusion; do not silently rewrite the history.
- Routine wording fixes are fine. Preserve substantive user edits and evidence.
- Keep entries concise but specific enough to reproduce and assess the learning.
- Never include credentials, secrets, or unnecessary personal information.
- Use plain language. Avoid template placeholders in the finished journal and
  references to the assistant, automation tooling, or conversation mechanics.

After writing, check the journal for factual support, chronological consistency,
working relative file references, unresolved placeholders, and claims that exceed
the evidence. Briefly report the file created or updated and any material gaps.
```
