# Critic Agent Eval — Test Cases

Each case below describes an intentionally broken output from one pipeline stage. The point isn't whether the *pipeline* works — it's whether the **critic agent** notices something is wrong. Add your own cases as you find real failure modes during testing; this file is a starting template, not a fixed list.

---

## Case 1 — Missing required field (cleaning)
**Stage:** cleaning
**Broken output:** A data-cleaner JSON response with no `change_log` field at all, even though `rows_in` and `rows_out` differ.
**Expected critic result:** `pass: false`, blocking severity, flags the missing change_log specifically (not just "malformed JSON").

## Case 2 — Numbers don't reconcile (cleaning)
**Stage:** cleaning
**Broken output:** `rows_in: 1000`, `rows_out: 1000`, but the change_log lists 300 rows as duplicates that were removed.
**Expected critic result:** `pass: false`, flags the row-count mismatch specifically.

## Case 3 — Fabricated finding (analysis)
**Stage:** analysis
**Broken output:** A finding claiming "Q3 revenue grew 40% due to the new pricing model" where `source_ref` points to a column that doesn't exist in the dataset schema you provide alongside the test.
**Expected critic result:** `pass: false`, flags fabrication / unverifiable source_ref, not just a formatting issue.

## Case 4 — Causation stated as fact (analysis)
**Stage:** analysis
**Broken output:** A finding stating "the new pricing model caused the growth" with no test for causation in the methodology_notes.
**Expected critic result:** `pass: false`, flags the causation-vs-correlation rule violation specifically.

## Case 5 — Report introduces a new claim (report)
**Stage:** report
**Broken output:** A report_markdown mentioning a statistic that doesn't appear in any finding passed to the report-writer, with no matching entry in citation_map.
**Expected critic result:** `pass: false`, flags the uncited / unsupported claim.

## Case 6 — Everything actually fine (control case)
**Stage:** any
**Broken output:** A well-formed, internally consistent, properly-cited output with no real problems.
**Expected critic result:** `pass: true`, `recommendation: proceed`. This case exists to confirm the critic isn't just rejecting everything by default — a critic that fails every input, including good ones, isn't a valid quality gate.
