# Eval Set: Critic Agent Error Detection

Purpose: verify the critic agent actually catches errors, rather than
rubber-stamping every report. Each test case is a draft report with a known,
deliberately injected error. Run these via `/run-eval` in Claude Code.

Add at least 5–8 cases before considering this "done." Vary the error type —
don't just test one failure mode.

---

## Test case template

```
### TC-01: [short description]

**Injected error type:** [fabricated number | wrong column referenced |
dropped caveat | overstated confidence | correct claim mislabeled as wrong]

**Draft report excerpt:**
[paste the specific claim/paragraph with the error]

**Ground truth:**
[what the data actually says]

**Expected critic verdict:** rejected
**Expected issue flagged:** [what the critic should say is wrong]
```

---

### TC-01: Fabricated statistic

**Injected error type:** fabricated number

**Draft report excerpt:**
_(fill in once you have a real draft report to base this on)_

**Ground truth:**


**Expected critic verdict:** rejected
**Expected issue flagged:**


---

### TC-02: Correct report (control case)

**Injected error type:** none — this should be approved

**Draft report excerpt:**


**Ground truth:**


**Expected critic verdict:** approved
**Expected issue flagged:** n/a

---

_Add more cases below as you build out the pipeline._
