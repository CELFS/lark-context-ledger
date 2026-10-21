# Records, tasks, and thinking notes

Save tasks, notices, reviews, and thinking notes under `output/reports/YYYYMMDD/<task-directory>/`. Start daily reading with the summary or thinking note. Working files go in `output/work/`, state in `output/state/`. The project ignores all output; the independent local report repository excludes attachments.

Read `report_language` from `config/sources.local.json`: default `zh`; supported values `zh` and `en`. Use it for authored summaries, advice, headings, status labels, and new document labels. The root `CHANGELOG.md` and report repository `LOG.md` are exceptions: both use English. Preserve original messages, quotations, names, and source titles. Existing documents and filenames are not translated or renamed automatically. Template labels illustrate meaning and must be rendered in the configured language, except for the English log format below.

Directory and filename examples in English instructions use English. They illustrate the format, not the actual output language. For new output, write authored topic text in directory and file names and document-type labels in `report_language`: Chinese for `zh`, English for `en`. Preserve actual source names. Keep structural names (`output`, `reports`, `work`, `state`, `attachments`), type markers (`topic`, `watch`, `thinking`), numbering, and date/time formats unchanged. Chinese naming examples are in [README.zh-CN.md](../README.zh-CN.md). These conventions apply to new output only; do not translate, rename, move, or regenerate existing reports merely to align them with the examples or a language setting change.

## Classification and relationships

- Specified communication: preserve sources and connect evidence about the same item across conversations without duplicating tasks.
- Company notices: record author, applicability, effective date, requirements, and related items. Mark applicability as unconfirmed when unclear.
- Task progress: distinguish submission, receipt, review, confirmation, and final delivery. One intermediate step does not prove completion.
- Exploration: record ideas, experiments, and questions as exploration. Analysis and suggestions do not become formal requirements automatically.
- Personal reflection (`thinking`): save explicitly requested reflection and self-reminder principles separately from work progress. See “Thinking notes” below.

Preserve existing stable item identifiers for evidence and state relationships, not directory names. Use one writer; resolve concurrent conflicts first. Moving a directory does not change item identity.

The summary's current understanding and task states are the daily maintenance entry point; the transcript supplies evidence. Do not maintain a separate competing task ledger. Keep tool development in the root `CHANGELOG.md`, actual usage history in `output/reports/LOG.md`, and concrete task progress in the corresponding report.

## States and evidence

Task states: action needed, reply needed, waiting on others, confirmation needed, completed, canceled. Notices, exploration, and thinking notes need not use task states. In Chinese reports use 待行动、待回复、等别人、待确认、已完成、已取消.

For tasks, keep a stable ID, item, state, owner, first discovery time, latest evidence, source message IDs and links, deadline, and suggested next step. If absent, explicitly label the deadline as unspecified and owner as unconfirmed, in the report language. Never default ownership to the user.

- The last speaker does not determine who owes a reply. Acknowledgment does not prove completion.
- Close an item only with explicit completion evidence or user confirmation. With incomplete records, say no explicit reply was observed or confirmation is needed; do not accuse the user of missing a reply.
- Keep completed and canceled items closed when old, forwarded, or duplicate messages reappear. Mark conflicting new evidence for review while preserving the closed state until confirmed.
- Do not execute or remind about user-canceled items. Silence or age does not imply cancellation or completion.
- Label old, uncertain items with evidence dates and uncertainty; do not present them as urgent.
- Separate formal requirements, user feedback, and analysis. Apply user corrections to the current understanding while preserving earlier wording and correction evidence.
- When new requirements replace old ones, record when, from whom, and with what impact. Do not erase the old requirement.

## Log ownership and entries

- Root `CHANGELOG.md`: tool changes to skills, rules, scripts, templates, and documentation. Keep conversation details, collection results, business conclusions, and report result links out of this file.
- `output/reports/LOG.md`: actual collection, organization, report generation, and report maintenance operations. Record the affected scope, result, verification or gaps, and related report references when useful. Keep detailed business progress in its topic or thinking note; the usage log is not another task ledger.
- Mixed work: split tool changes and actual usage into their respective logs. Tool development alone does not establish a successful collection or report run. Do not infer completed operations from a request, silence, or a partial result.

Both files use English regardless of `report_language`; task-level progress within reports still uses the configured report language. The tool repository defines the convention and reusable format here; actual usage entries belong in the report repository, not in a tracked example or template.

Use `YYYY-MM-DD HH:mm +08:00` for new entries, distinguishing operation time from recording time when different. Each entry covers one change or operation, usually with 2–4 short bullets containing only meaningful fields. During migration, retain the precision of historical dates and do not invent missing times.

```markdown
## YYYY-MM-DD HH:mm +08:00 — Change or operation

- Change: what happened and the evidence.
- Confirmed / unresolved: current understanding and gaps.
- Next step: suggested user action; omit when unnecessary.
- Source: message reference and related item file.
```

Append usage results after the operation, including failures or partial coverage when relevant. Reuse the existing `output/reports/LOG.md`; do not overwrite its history. Preserve historical records when splitting or translating logs, and do not translate existing reports as a side effect. Do not copy chats or entire task lists into either log. Provide sufficient context in the report. Cite only necessary excerpts with speaker and time; do not present hearsay as a direct commitment.

## Directory naming

The outer `YYYYMMDD` is the creation date. Tasks created on the same day share that directory. Subdirectories use:

- Topic summary: `NN-topic-MMDD_HHmm-MMDD_HHmm-topic-source/`, with message start and end times.
- Ongoing monitoring: `NN-watch-MMDD_HHmm-topic-source/`, with message start time only.
- Personal reflection: `NN-thinking-topic/`, without a message time range or a required chat source.

NN is a two-digit daily creation sequence shared across all three types; append without renumbering. Use UTC+8 and `-` as the range separator for conversation time ranges. Keep actual group or private-chat names when naming conversation records. Ongoing updates keep the original date and directory; record latest coverage inside the documents. Updates to the same thinking note also keep its original date and directory. The directory type does not authorize monitoring or subscription setup. Mirror task working files under `output/work/YYYYMMDD/<task-directory>/`.

## Two documents

Conversation tasks (`topic` and `watch`) use the two-document layout below. Thinking notes use the single-document layout in “Thinking notes”.

Filenames contain preparation date `YYYYMMDD`, source or specific topic, and document type. State the message coverage in the document. The following examples use English labels for `report_language: "en"`; use the configured language for new authored labels while preserving source names and existing filenames.

- `YYYYMMDD-topic-summary.md`: necessary background, current understanding, key changes, unresolved questions, and next steps. Explain topics separately, with short date-and-speaker links. Omit CLI fields, long URLs, collection statistics, and internal process details.
- `YYYYMMDD-topic-transcript.md`: chronological messages from the range, each once, with speaker, timestamp, and reply relationships. Preserve full original bodies. Reference the same message across topics without copying it repeatedly. Internal IDs may be hidden anchors, not visible fields.
- `attachments/`: save each original attachment once and link to it; do not repeat its full contents. Exclude attachments from Git.

Explain scope and material completeness limitations once. Use the transcript for verification and the summary for daily work. Update summaries and incremental originals instead of rereading or rewriting all accumulated material every run.

## Thinking notes

Save a thinking note only when the user explicitly requests saving or confirms the proposed save. Ordinary discussion, venting, or asking for advice does not authorize writing the user's views into a note or business report.

- Save one dated file, `YYYYMMDD-topic.md`, under `NN-thinking-topic/`. The example uses English; write new topic text in the configured report language. Identify its type as `thinking`, preparation date, and discussion source in the configured report language.
- Keep reusable self-reminder principles and the supporting discussion together when requested. State the triggering context, distinguish observations from interpretations, and preserve uncertainty.
- Link related topics and available evidence without duplicating their transcripts. A separate transcript and attachment directory are not required; reuse existing originals and attachments when relevant.
- Use material supplied in the conversation or already authorized and collected. A request to save reflection does not authorize additional Lark reads; follow collection rules if new collection is separately requested.
- Follow the personal reflection boundaries in [communication.md](communication.md). Saving a note does not make its principles project rules, permanent user preferences, or assigned tasks.

Write the note directly as Markdown. The conversation collector and two-document builder are not required for thinking notes; do not invent chat IDs, time ranges, or a conversation index to fit their format. Existing reports and directories remain unchanged unless the user requests migration.

## Execution

The collection and document-building steps below apply to conversation archives. For thinking notes, follow “Thinking notes” above and verify the saved content and references.

1. Keep the task request, scope, and process in `output/work/YYYYMMDD/<task-directory>/`, not README, skill, or reusable rules.
2. Collect authorized sources incrementally with `scripts/sync.py`, complete pagination, deduplicate, and save cursors. Read batches of at most 100 messages from `output/work/sources/`.
3. Compare forwarded backups only when useful, using `scripts/reconcile_backup.py`. Forward time differs from original message time. Without original IDs, describe text comparison rather than claiming ID-level equivalence.
4. Organize topics from full context and preserve changes and uncertainties. Topic organization does not require repeating original messages. State inaccessible sources, recalls, or missing attachments; do not silently substitute sources.
5. Prepare the reviewed index and summary draft in the configured report language under the task working directory. `scripts/build_document.py` saves the transcript and summary in the report directory. It localizes transcript labels but copies the draft without translating it. Reuse originals and attachments; do not rebuild collection infrastructure per task.
6. Check coverage, original preservation, relationships, and links. Do not repeat full validation without a new concern. Simplification must not delete evidence or close unfinished items.

The AI-maintained index uses chats, start/end, topics, and excluded for review validation. output and summary_output name two distinct files in the same report directory; reading_draft points to the reviewed summary; resource_index optionally locates attachments. Language comes from the local config, not an additional manifest override. The user only maintains the simple local configuration.

Keep internal versions, pending fingerprints, and collection evidence local and out of the final narrative. Do not clear pending messages before saving analysis or when a message changed during analysis.
