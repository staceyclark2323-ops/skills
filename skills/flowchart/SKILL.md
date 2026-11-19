---
name: flowchart
description: "Turn a process, procedure, or how-to document into a clean step-by-step decision flowchart: a Start oval, numbered action boxes, a yes/no diamond after every step (\"Step complete?\"), red No branches that loop back to fix the step, and a Done oval. Use when the user types /flowchart, or asks for a flowchart, decision diagram, process map, or step-by-step visual of a document, book, or procedure (for example, the steps of writing IEP goals in Infinite Campus)."
---

# /flowchart: step-by-step decision diagram

Turns the steps in a source (an attached document, pasted text, or the
user's own list) into one printable flowchart image. Think of it like a
recipe card with a taste test after every step: do the step, check it,
and if it isn't right yet, go back and fix it before moving on.

## What the finished visual looks like

```
        ( START: first thing you open/do )
                      |
             [1  Action box     ]  <-------------+
             [   • key sub-step ]                |
                      |                    Fix, then re-check
                 < Step done? > --No-->  [ What to do if not ]
                      | Yes
             [2  Action box     ]  <-------------+
                     ...
        ( DONE: final outcome )
```

- **Ovals (green):** start point and final outcome
- **Blue boxes, numbered:** one action per step, with 0-3 short sub-bullets
- **Amber diamonds:** a yes/no check after every step
- **Red boxes and arrows:** the "No" path, which says what to fix and loops
  back to that step
- Crisp sans-serif labels on a white background, so it prints cleanly

## Inputs

1. **Source content.** Use the attached or pasted document. If nothing is
   attached and the user didn't list the steps, ask for the document. Never
   invent steps for a real procedure.
2. **Title.** If the user gives a title, use it exactly, even when the
   document is named something else. Otherwise use the document's title.

## Steps

1. **Read the whole source.** Pull out the procedure in order. Keep the
   source's own wording for button names, tabs, and menu paths (for example
   *Student Information > Special Ed > Documents*).
2. **Group it into 4-10 main steps.** A step is something a person finishes
   before moving on. Merge tiny clicks into the step they belong to and put
   the important ones in `details` (at most 3 bullets, each under ~12 words).
3. **Write each step's check and No path.**
   - `check`: a short yes/no question, at most ~5 words, ending in "?"
     (e.g. "Baseline data entered?"). Default is "Step N complete?".
   - `if_no`: one plain sentence saying what to do, drawn from the source
     when it gives a fix or common mistake (e.g. "Add the baseline from
     present levels, then save").
4. **Set the start and end.** `start` is where the person begins (e.g. "Log
   in and open the student's IEP"). `end` is the real outcome (e.g. "Goals
   saved and ready for the IEP meeting").
5. **Write the spec** as JSON in the scratchpad (see
   `examples/sample_spec.json` for the exact shape):
   ```json
   {"title": "...", "subtitle": "optional", "start": "...",
    "steps": [{"action": "...", "details": ["..."], "check": "...?", "if_no": "..."}],
    "end": "..."}
   ```
6. **Render it:**
   ```bash
   python3 <skill-dir>/scripts/render_flowchart.py spec.json <out-basename> --png
   ```
   This writes `.svg`, `.html`, and `.png` (2x resolution, good for slides
   and printing). The PNG step uses Python Playwright, or Node's Playwright
   if Python's isn't installed.
7. **Check it.** Open the PNG and confirm every label is readable, nothing
   overlaps, and the step order matches the source. If a label is too long,
   shorten it in the spec and re-render rather than shrinking text.
8. **Deliver it.** Send the PNG, and publish the HTML as an artifact if the
   user wants a shareable link. Give a 2-3 sentence plain-language summary of
   the steps; don't paste the JSON unless asked.

## Writing style for labels

- Start action boxes with a verb: "Enter baseline data", not "Baseline data".
- Use the words a teacher or staff member would say out loud, not jargon
  the source doesn't use.
- No step should need the reader to scroll back to understand it.

## If the user wants a different look

The renderer covers the standard top-to-bottom decision chart. For a
different layout (left-to-right, swimlanes, branching paths that don't
loop back), hand-draw it as inline SVG in an HTML artifact using the same
color meanings: green start/end, blue actions, amber decisions, red fixes.
