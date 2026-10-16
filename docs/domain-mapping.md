# Domain Mapping

Fill in names and use this as a checklist while studying — each box maps to something you had to actually build, which is stickier than just reading about it.

## Person A — Orchestration & Context Lead: ___________

**Exam domains:** Agentic Architecture & Orchestration (27%), Context Management & Reliability (15%)

- [ ] Can explain agents vs. workflows vs. conversational systems, and why this project needed which
- [ ] Implemented the agent loop (gather context → take action → verify results)
- [ ] Chose and can justify an orchestration pattern (pipeline / supervisor-worker / hub-and-spoke)
- [ ] Designed the context strategy: what's compacted, what persists, what's passed in full
- [ ] Can explain what happens if context runs out mid-pipeline and how we handle it

## Person B — Tool & MCP Lead: ___________

**Exam domains:** Tool Design & MCP (18%)

- [ ] Built a working custom MCP server
- [ ] Can explain the schema design choices for each tool (naming, descriptions, parameters)
- [ ] Understands `tool_use` vs `end_turn` stop reasons and where they show up in this project
- [ ] Designed clear error returns from tools (not just crashes)
- [ ] Can explain the trade-off of tool-based data access vs. dumping raw data into context

## Person C — Claude Code & Prompt Lead: ___________

**Exam domains:** Claude Code (20%), Prompt Engineering (20%)

- [ ] Set up the Claude Code workspace and at least one custom slash command
- [ ] Wrote system prompts for all four agents with structured (JSON) output
- [ ] Used few-shot examples where they meaningfully improved output
- [ ] Built an eval set that tests whether the critic agent catches injected errors
- [ ] Can explain how prompt design changed after seeing real failure cases

## Shared (everyone should be able to speak to)

- [ ] Why we chose this orchestration pattern over the alternatives
- [ ] Where the pipeline is most likely to fail, and how we'd harden it for production
- [ ] What we'd change if the dataset were 100x larger
