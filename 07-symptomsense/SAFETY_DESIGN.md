# SymptomSense — Safety Design Document

> This document explains every safety decision
> made in building SymptomSense.
> Written by the developer as a record of
> intentional design choices, not an afterthought.

---

## The Core Principle

**SymptomSense is a triage tool, not a diagnostic tool.**

The difference:
- Diagnosis = "You have condition X"
  (requires physical exam, medical history, tests)
- Triage = "Given these symptoms, here is
  the appropriate level of care to seek"
  (requires pattern recognition + escalation logic)

LLMs are capable of the second.
They are not qualified to do the first.
Every design decision flows from this distinction.

---

## Safety Layers — In Order of Execution

### Layer 1 — Input Validation (Pydantic)
**What it does:** Rejects malformed inputs before
any processing begins.

**Decisions made:**
- Minimum 10 characters for symptoms —
  prevents gaming with single-word inputs
- Maximum 2000 characters —
  prevents prompt injection via very long inputs
- Severity must be 1–10 —
  forces structured severity communication
- Age is required — triage logic differs
  significantly by age group

**Why Pydantic over manual checks:**
Pydantic validators run automatically on every input.
They cannot be bypassed by callers.
Manual if/else checks can be forgotten.
Pydantic cannot.

---

### Layer 2 — Red Flag Pre-Check (Rule-Based)
**What it does:** Scans symptom text for emergency
keywords BEFORE calling the LLM.
Returns SEEK_EMERGENCY immediately if found.

**Why rule-based instead of LLM:**
LLMs are probabilistic — they can hallucinate,
misclassify, or fail to detect critical signals
under certain input conditions.
Rule-based keyword matching is deterministic.
It cannot hallucinate.
For life-critical emergency detection,
deterministic > probabilistic.

**The 34 emergency keywords include:**
- Chest pain / pressure / tightness
- Breathing difficulty
- Stroke signs (face drooping, arm weakness)
- Loss of consciousness
- Suicidal thoughts
- Overdose / poisoning

**Design decision — false positives are acceptable:**
If someone mentions "chest pain" in a historical
context ("my chest pain last year has resolved"),
they will get a SEEK_EMERGENCY result.
This is intentional. The cost of a false positive
is an unnecessary doctor call. The cost of a false
negative is a life. We optimize for false positives.

---

### Layer 3 — Constrained LLM Prompt
**What it does:** Instructs Gemini with explicit
positive AND negative constraints.

**Positive constraints (what to do):**
- Return only one of 3 triage levels
- Explain reasoning without naming conditions
- List red flags to watch for
- Suggest safe general actions

**Negative constraints (what never to do):**
- Never diagnose
- Never name specific conditions
- Never recommend medications or dosages
- Never use phrases: "you have", "this is",
  "sounds like"
- Never downplay symptoms that could be serious

**Escalation rule in prompt:**
"When uncertain between two triage levels,
ALWAYS escalate to the higher level."
This is stated explicitly in the system prompt —
not assumed.

---

### Layer 4 — Output Validation (Pydantic)
**What it does:** Validates LLM output before
showing to user.

**Key validators:**
- triage_level must be one of 3 valid values
  — defaults to SEE_DOCTOR (not MONITOR_HOME)
  on invalid value
- urgency_score clamped to 1–10
- disclaimer enforced — cannot be empty
- medication keywords stripped from
  immediate_steps automatically

**Why default to SEE_DOCTOR not MONITOR_HOME:**
When validation fails, we don't know why.
The safe assumption is to escalate, not downgrade.
SEE_DOCTOR is the middle ground — not alarming,
but not dismissive.

---

### Layer 5 — Medication Keyword Filter
**What it does:** Post-LLM scan of immediate_steps.
Removes any step containing medication references.

**Why this exists:**
Even with explicit negative constraints in the
prompt, LLMs occasionally include medication
suggestions in edge cases.
This post-processing filter is a hard backstop.
If a step mentions "mg", "tablet", "ibuprofen",
"paracetamol", or similar — it is removed and
replaced with safe general guidance.

---

### Layer 6 — Mandatory Disclaimer
**What it does:** Enforces disclaimer text
on every single response.

**Design decision:**
The disclaimer is not optional and cannot be
removed by the LLM. Even if Gemini omits it,
the Pydantic validator adds it back.
It is hardcoded in the output rendering
in the UI as well — a second enforcement point.

---

### Layer 7 — Always-Visible Emergency Numbers
**What it does:** Emergency contact numbers
are displayed on EVERY page, not just on
SEEK_EMERGENCY results.

**Why:**
If someone misreads a SEE_DOCTOR result
as "I'm fine", the emergency number is still
visible. The number is displayed regardless
of triage outcome.

---

## What This System Will NOT Do

These are hard limits that no user input,
prompt injection, or edge case can override:

| Will never do | Why |
|---|---|
| Diagnose a condition | No physical exam possible |
| Recommend medications | Wrong dose = direct harm |
| Say "you are fine" | Cannot know this |
| Override emergency escalation | Life safety |
| Remove the disclaimer | Legal + ethical |
| Work without showing emergency numbers | Always present |

---

## Known Limitations

1. **No medical history context** — the system
   does not know the user's existing conditions,
   allergies, or current medications. This limits
   triage accuracy.

2. **Text only** — cannot observe physical
   appearance, skin color, breathing pattern,
   or other visual indicators a real triage
   nurse would use.

3. **Self-reported severity** — severity scores
   are subjective. A 7/10 for one person is a
   3/10 for another.

4. **Language limitations** — the red flag
   keyword scanner works in English only.
   Non-English descriptions of emergency symptoms
   may not trigger the pre-check.

5. **Not a substitute** — this tool is designed
   to reduce unnecessary ER visits for
   non-emergencies and to encourage appropriate
   care-seeking for moderate symptoms.
   It is not designed to replace any part of
   the medical system.

---

## If I Were Building This for Production

1. Add a "this is urgent but I can't go to ER"
   pathway — connect to telehealth APIs
2. Store no user data — all triage is stateless
3. Add HIPAA compliance review before any
   real deployment
4. Partner with medical professionals to
   validate the triage logic
5. Add a feedback loop — "was this triage
   correct?" to improve the system over time
6. Build in multiple language support for
   the red flag scanner

---

*This document was written as part of a
14-day AI build-in-public challenge.
SymptomSense is a demonstration of
responsible AI design principles —
it is not a production medical tool.*