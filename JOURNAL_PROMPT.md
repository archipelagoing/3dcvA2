# Work Log Prompt

Copy the prompt below into a conversation in any repository. Use it to create
`JOURNAL.md` and maintain one concise entry after each work session.

```text
Create or update JOURNAL.md as a chronological work log for this repository.

Read the project checklist (TODO.md or its existing equivalent), current request,
relevant project files, and existing journal before writing. Keep one authoritative
journal and preserve substantive user edits.

Write ONE entry per work session/request, even when it covers several TODO sections.
Do not split one session into separate entries for each task or experiment. Update
that session's entry as work proceeds, and finish it before reporting completion.
Read entries oldest to newest to see what was attempted and how each session ended.
Ordinary discussion does not need an entry unless it includes an investigation,
new evidence, or a decision affecting the work.

Use exactly this simple structure:

## 01 — Short description of the session
Date: YYYY-MM-DD
TODO items covered: Actual item labels such as 1c–1h and 2a, or section names if
labels are unavailable. State when the work was documentation-only.

### What was tried
- Concrete actions, approaches, inspections, or experiments attempted this session.
- Include commands and parameters only when useful for understanding or repeating work.

### What worked
- Successful changes and checks, with actual results and relative links to evidence.
- Identify completed TODO items and explain the practical result briefly.
- Distinguish verified outcomes from promising approaches that remain untested.

### What did not work
- Failed attempts, relevant errors, limitations, blockers, and unfinished checks.
- Include the fallback and its outcome when one was tried.
- State what remains open and why. If nothing failed, say so; do not invent failures.

Rules:
- Number entries consecutively and put the oldest first. Use the actual date;
  do not invent dates, results, commands, or completed work.
- Cover all TODO items attempted in the session, including partial progress.
- Keep the three headings above; do not add separate background, evidence,
  lessons, uncertainty, or decision sections. Put useful details under the
  appropriate heading instead.
- Keep entries concise and factual, with enough evidence to assess the outcome.
- Update the checklist separately so its checkboxes reflect actual completion.
- Never mark a task complete solely because it was discussed or code was written.
- Link to repository files using portable relative paths where possible.
- Preserve failed attempts that explain why another approach was chosen.
- If a later session corrects an earlier conclusion, record that correction in
  the new entry and link back. Do not silently rewrite the historical result.
- When initializing from past records, label reconstructed entries as retrospective.
  Use only supported history. If session boundaries are unknown, say so instead
  of inventing separate sessions.
- Never prewrite future sessions as completed work. Keep planned work in the checklist.
- Log setup does not authorize executing the backlog or taking external actions.
- Exclude secrets, unnecessary personal information, and references to the
  assistant or automation tooling. Use “session” to describe each run.

Check the final file for unsupported claims, missing attempted TODO items,
incorrect chronology, broken local references, and leftover template placeholders.
Briefly report the journal updated and any material blockers.
```
