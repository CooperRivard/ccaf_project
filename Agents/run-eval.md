---
description: Test whether the critic agent actually catches injected errors, using the cases in eval/test_cases.md.
---

Read every test case in `eval/test_cases.md`. For each one:

1. Take the case's "broken output" exactly as written and pass it to the **critic** subagent as if it were real output from the stage the case specifies.
2. Record: did the critic mark it `pass: false`? Did its `recommendation` match what the test case expects? Does its stated `issues` description actually name the real problem, or did it catch something else by coincidence?
3. After all cases have run, report a summary table: case name, expected result, actual result, pass/fail — plus a final tally (e.g., "7/8 injected errors caught").

Do not modify the critic agent to make it pass these tests — if it's failing, that's a finding to report, not a bug to quietly fix before showing the group.
