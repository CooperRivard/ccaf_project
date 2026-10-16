---
description: Run the full raw-data-to-verified-report pipeline, with a critic check gating every stage.
argument-hint: [path-to-raw-dataset]
---

Run the full pipeline on the dataset at: $ARGUMENTS

Follow this sequence exactly, and do not skip a critic check under any circumstances:

1. Delegate to the **data-cleaner** subagent with the raw dataset path above.
2. Delegate to the **critic** subagent to review the data-cleaner's output (stage: "cleaning").
   - If `recommendation` is `retry`: re-run the data-cleaner, appending the critic's `issues` as explicit feedback. Allow at most 2 retries before escalating to the user.
   - If `recommendation` is `escalate_to_human`: stop immediately and report the issue to the user in plain language.
3. Once cleaning passes, delegate to the **data-analyst** subagent with the cleaned data path and change log.
4. Delegate to the **critic** subagent again (stage: "analysis"). Apply the same retry/escalate logic as step 2.
5. Once analysis passes, delegate to the **report-writer** subagent with the validated findings.
6. Delegate to the **critic** subagent one final time (stage: "report"). Same retry/escalate logic.
7. Present the final report to the user, followed by a short summary: how many retries occurred at each stage and why, so the group can see where the pipeline struggled.
