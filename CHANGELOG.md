# lark-context-ledger changelog

Tool changes only: skills, rules, scripts, templates, and documentation. Actual collection, report generation, and report migration records belong in `output/reports/LOG.md`. Entries are written in English. Historical date-only entries retain their original precision; the logging rules at each date describe the convention in force then.

## 2026-10-20 — Establish initial rules and templates

- Change: add the repository entry point, local skill, collection and task rules, communication review rules, and record templates.
- Boundary: Lark access is strictly read-only; AI cannot send messages or perform remote business operations. Suggestions are provided to the user only.
- Initial setup: conversation sources, collection windows, and the historical start date were not configured; automatic collection and monitoring were not enabled.
- Source: the user's initial request; see [AGENTS.md](AGENTS.md).

## 2026-10-20 — Separate local collection configuration and unify output paths

- Change: add an example JSON and an empty local JSON. Real sources must come from the local configuration; document the fields and reading rules.
- Storage: at this stage, only `config/sources.local.json` was ignored; runtime data, records, and reports were placed under `output/`, which was not yet ignored.
- Initial setup: no real sources, synchronization script, or Lark calls were present.
- Source: the user's confirmation; see [config/sources.md](config/sources.md).

## 2026-10-20 — Simplify configuration to a date and names

- Change: retain only `since` and `chats`; users do not maintain conversation IDs.
- Resolution: allow read-only lookup of specified group or contact names, require confirmation for ambiguous matches, and save mappings in `output/state/chat-map.json`.
- Initial setup: the local configuration remained empty; name resolution and synchronization scripts were not yet implemented, and no Lark query was made during this change.

## 2026-10-20 — Add manual collection and topic archive workflows

- Change: add `scripts/sync.py` and `scripts/build_document.py`, with rules for topic-based originals and separate summary sections.
- Validation: offline checks passed; live collection still required application configuration and read-only login.
- Storage: keep concrete task requests and execution progress under `output/`, outside reusable rules.

## 2026-10-20 — Add backup reconciliation and handle CLI response details

- Change: add the local backup reconciliation script and handle returned timestamp formats, empty results, and message ordering.
- Boundary: keep source-specific collection limitations and execution results with local task records; the tool does not enable automatic scheduling or remote writes.
- Storage: keep actual outputs and their scope under `output/`; README files do not contain concrete task details.

## 2026-10-20 — Separate task documents from reusable rules

- Change: move task-specific execution instructions under `output/` and consolidate reusable archive procedures into the record rules.
- Historical convention: README files describe the repository; the root `LOG.md` then held business-free maintenance and execution entries. The later log split supersedes that convention.
- Validation: update affected references while preserving original records and archived outputs.

## 2026-10-20 — Simplify task output and tracking scope

- Change: define a daily summary and one chronological transcript, with attachments linked separately.
- Storage: retain working files, synchronization state, and attachments locally with Git exclusions; keep previous document versions in the working directory.
- Execution: records of regenerating existing reports are maintained in the report repository log.

## 2026-10-20 — Define output document filenames

- Change: include preparation date, source or specific topic, and document type in filenames, initially using Chinese labels.
- Compatibility: preserve message relationships when updating document links and generation configuration.

## 2026-10-20 — Organize task directories by date, type, and message range

- Change: organize tasks by creation date and daily sequence; use `topic` for summaries and `watch` for ongoing monitoring, with hyphens in time ranges.
- Storage: update reference and attachment exclusion conventions while preserving originals, summaries, and attachments during migrations.
- Boundary: `watch` defines a directory format only; this change did not enable scheduling or call Lark.

## 2026-10-20 — Rename the project and report output directory

- Change: rename the project and local skill to `lark-context-ledger`, set the report destination to `output/reports/`, and update documentation and internal index references.
- Storage: ignore all `output/` in the project repository; reserve the report directory for independent local version control with attachments excluded. The user performs initialization and commits.
- Execution: report and attachment preservation during the migration is recorded in the report repository log.

## 2026-10-20 — English instructions and configurable report language

- Change: maintain reusable instructions and code comments in English and add a Chinese README. Reports default to zh; local JSON may select zh or en.
- Behavior: localize transcript labels and author summaries in the configured language; preserve source messages, historical reports, and existing filenames.
- Boundary: local changes only; no Lark calls or Git mutations.

## 2026-10-21 14:33 +08:00 — Document independent thinking notes

- Change: add thinking note routing, shared daily numbering, and a single-document layout across the skill, rules, and usage documentation.
- Boundary: save personal reflection only when requested; note creation does not authorize collection or establish project rules, permanent preferences, or tasks.
- Scope: documentation only; collection scripts and existing records remain unchanged.

## 2026-10-21 14:46 +08:00 — Separate tool changes from usage history

- Change: rename the root `LOG.md` to `CHANGELOG.md`, retain tool-related history, and move collection and report operation entries to `output/reports/LOG.md`.
- Language: translate the migrated history into English; both logs use English independently of `report_language`. Business reports and thinking notes retain their configured language.
- Documentation: align the skill, record rules, repository instructions, and both README files with the log split. Keep the reusable entry format in the record rules.
- Preservation: retain original dates and all historical details across the two logs; do not invent missing times or alter existing reports.

## 2026-10-21 15:55 +08:00 — Separate README naming examples by language

- Change: use English report filename examples in the English README and Chinese examples in the Chinese README, with links between the two versions.
- Readability: move directory descriptions below the trees to keep path examples compact.
- Scope: documentation only; retain the configured report language, Chinese default, and existing filenames.

## 2026-10-21 16:05 +08:00 — Align naming rules with README language separation

- Change: use English filename examples in record rules and distinguish documentation examples from actual output naming across the repository instructions, configuration guide, and local skill.
- Language: new authored topic text and document-type labels follow `report_language`; preserve source names, structural names, type markers, and date/time formats.
- Preservation: do not translate, rename, move, or regenerate existing reports to match examples or language setting changes. No existing reports were changed.

## 2026-10-21 16:28 +08:00 — Restore concise directory descriptions

- Change: add short inline descriptions to the directory trees in both README files for easier scanning.
- Preservation: retain language-specific filename examples and the detailed explanations below each tree.
