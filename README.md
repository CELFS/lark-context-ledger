# lark-context-ledger

English | [简体中文](README.zh-CN.md)

A personal work context ledger built on Lark CLI. Collect communication, preserve context, track local task progress, and review communication to identify alignment gaps early. Lark and Feishu access is strictly read-only: AI never sends messages or modifies remote business data.

## Everyday use

Set a start date and chat names in `config/sources.local.json`, then ask for a topic summary, progress update, or communication review. Names are resolved internally; ambiguous matches require confirmation.

Ask explicitly to save a personal reflection as `thinking` when you want to keep discussion and self-reminder principles for later reading. Ordinary discussion does not save your views automatically or authorize Lark collection.

Conversation tasks provide two documents; thinking notes use one dated Markdown file:

```text
output/
  reports/YYYYMMDD/
    NN-topic-MMDD_HHmm-MMDD_HHmm-topic-source/
      YYYYMMDD-主题-整理稿.md       Daily reading: background, conclusions, changes, next steps
      YYYYMMDD-主题-原文归档.md     Evidence: speakers, timestamps, messages, reply relationships
      attachments/                Local only, excluded from the report repository
    NN-watch-MMDD_HHmm-topic-source/  Ongoing monitoring, start time only; same document layout
    NN-thinking-topic/
      YYYYMMDD-主题.md             Personal reflection: principles, discussion, and source links
  work/                           Working materials, ignored by the project repository
  state/                          Collection state, ignored by the project repository
```

The outer date is the creation date. NN is a shared daily sequence across all three types; append without renumbering. `topic` includes message start and end times; `watch` includes only the start time; `thinking` does not require a message time range or chat source. Ongoing conversation updates keep the original directory and record the latest coverage inside the documents. Updates to the same thinking note also keep its original directory. All times use UTC+8. Naming a directory `watch` does not activate monitoring. Task working materials mirror the date and directory name under `output/work/`.

Conversation filenames include the preparation date, source or specific topic, and document type. The examples show the default Chinese naming; use the configured report language for new document labels. Preserve actual source names. Existing filenames remain unchanged. Keep each original message once, link attachments without repeating their full contents, and read the summary first. Reuse collected data and update incrementally.

A thinking note links related topics and existing evidence without copying transcripts. Its principles remain personal reflection; they do not automatically become project rules, permanent user preferences, or tasks. Save thinking notes directly as Markdown; the conversation collector and two-document builder are not required.

README files describe the project and usage only. Task-specific requests and results belong in `output/`. The root `LOG.md` records maintenance or execution changes without business content.

The project repository ignores all of `output/`. The user may initialize `output/reports/` as a separate local Git repository to keep report history, without configuring a remote. Its own `.gitignore` excludes attachments. Working materials and collection state are outside the report repository. Git initialization and commits are performed by the user.

## Configuration and commands

The real configuration is `config/sources.local.json`, excluded from Git. See [configuration](config/sources.md) and the [example](config/sources.example.json). Required fields: `since` and `chats`. Optional: `report_language`, default `zh`; supported values are `zh` and `en`. Examples are never used as runtime configuration or authorization.

AI writes summaries, advice, and new report titles in the configured report language. The document builder switches transcript labels and explanatory text. Original messages, quotations, names, and source titles remain unchanged. Changing the setting does not translate existing reports or rename files. Repository instructions are maintained in English; reports still default to Chinese.

Run these commands from the repository root using Python's standard library and an authorized Lark CLI:

```bash
python3 scripts/sync.py status
python3 scripts/sync.py collect --chat 'Configured chat name'
python3 scripts/sync.py export --chat 'Configured chat name'
python3 scripts/build_document.py 'output/work/YYYYMMDD/task-directory/topic-index.json'
```

Use `sync.py resolve` to resolve names. Compare a forwarded backup with `reconcile_backup.py --source 'Group name' --backup 'Person name' --day YYYY-MM-DD`. Scripts collect and save data; AI reads the evidence and prepares the summary. No scheduled execution or continuous listener is enabled.

## Rules

[Boundaries](AGENTS.md) · [Local skill](.agents/skills/lark-context-ledger/SKILL.md) · [Collection](rules/sync.md) · [Records](rules/records.md) · [Communication review](rules/communication.md) · [Maintenance log](LOG.md)
