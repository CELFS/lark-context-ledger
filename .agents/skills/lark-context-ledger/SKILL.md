---
name: lark-context-ledger
description: Collect authorized Lark or Feishu conversations, organize work context and local task progress, and review communication for alignment gaps. Use for chat summaries, background reconstruction, progress updates, and personal communication reviews. Never send messages or modify remote business data.
---

# Work context ledger

Follow [AGENTS.md](../../../AGENTS.md). All state updates are local, and suggestions are for the user to act on.

Read `report_language` from `config/sources.local.json`: default `zh`, supported values `zh` and `en`. Write summaries, advice, and new report labels in that language. Preserve original messages and quotations. English instructions do not change the Chinese report default. Do not automatically translate existing reports or rename files.

## Read only what is needed

- Collection or monitoring: read [configuration](../../../config/sources.md), the real local JSON, and [collection rules](../../../rules/sync.md). Before using Lark CLI, read the installed `lark-shared` and relevant domain skill. Their sending or writing capabilities do not grant authorization here.
- Notifications, context, or tasks: read [record rules](../../../rules/records.md) and use [the topic template](../../../templates/topic.md).
- Alignment, efficiency, wording, attitude, or personal communication: read [review rules](../../../rules/communication.md) and use [the review template](../../../templates/review.md).
- Complete discussion archives: follow “Two documents” in the record rules. Save the request and scope in `output/work/YYYYMMDD/<task-directory>/archive.md`; collect and organize the evidence into a daily summary and a separate transcript. Keep task details out of this skill.

## Execution

1. Identify whether this run is collection, organization, or review. Start with new evidence, user feedback, and the current summary. Read historical transcripts and attachments only when needed.
2. Check sources, time ranges, message references, and context. State evidence gaps; do not invent missing details. Never collect from unconfirmed sources.
3. Merge new evidence into existing items. Distinguish tasks, notices, and exploration; suggestions do not become formal requirements automatically.
4. Save final documents in `output/reports/YYYYMMDD/<task-directory>/`, working materials in `output/work/`, and collection state in `output/state/`. The project ignores all output; the separate local report repository excludes attachments. Keep task changes within output and business-free maintenance notes in the root LOG.
5. Verify traceable sources, preserved closed states, evidence-based owners and deadlines, and absence of remote writes.
6. Answer direct user questions. Background reminders are only for meaningful progress, task changes, required action, or collection failures. Stay silent when unchanged; never promise continuous monitoring before it exists.

When access, permissions, or evidence are incomplete, retain prior local state and explain the gap. Do not broaden the scope, switch identities, or report false success.
