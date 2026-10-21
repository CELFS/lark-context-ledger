# Collection configuration

Use `config/sources.local.json` for real configuration. It is Git-ignored. The tracked [example](sources.example.json) documents the format only; its dates and names do not authorize collection and are never used at runtime.

## Fields

- `since` (required): initial collection date, `YYYY-MM-DD`, starting at 00:00 UTC+8. Later runs use the saved per-chat cursor; changing this field does not reset prior collection history.
- `chats` (required): an array of group names or colleague names. Only listed sources may be collected. Removing a source stops future collection while preserving existing records.
- `report_language` (optional): `zh` for Chinese or `en` for English. Default: `zh` when omitted. Other values, including empty or null, are invalid and stop execution.

Read the user-maintained local JSON before running. Invalid JSON, missing or invalid dates, and blank names stop collection. An empty chat list makes no Lark calls. Do not fall back to example values or guess dates and sources.

The report setting controls AI-authored summaries, advice, headings, and new document labels. The builder localizes transcript labels and explanatory text; it copies the reviewed summary draft without translation. Original messages, quotations, names, and source titles remain in their source language. Changing the setting does not automatically translate old reports or rename existing files. The author prepares new titles and drafts in the configured language; a previously prepared draft needs explicit revision before rebuilding in another language.

English documentation uses English directory and filename examples. Actual new output uses `report_language` for authored topic text in directory and file names and document-type labels; source names remain unchanged. Structural names, type markers, and date/time formats stay fixed as specified in [record rules](../rules/records.md). Documentation language does not override the `zh` default. Do not translate, rename, move, or regenerate existing reports to match these examples or a changed language setting.

Purpose and analysis requirements belong in Markdown rules. Users do not maintain IDs, types, versions, enable flags, or confirmation metadata. Scheduling and execution policy require separate confirmation.

## Name resolution

Look up only the basic group or contact information needed to resolve names in `chats`. Do not read other conversations or enumerate all chats or contacts.

Save unique, explicit matches. For duplicate names, group/contact collisions, or fuzzy matches, show the minimum identifying information and wait for user confirmation before reading that source. If not found, report the gap without broadening the search or creating a conversation.

Store resolved chat IDs in `output/state/chat-map.json`. A contact identifier is not a chat ID; verify through read-only methods. Never send a message or create a chat to obtain an ID. If read-only lookup cannot resolve it, stop and explain.

Recheck invalid or ambiguous mappings after name changes; do not automatically bind to another conversation. Old mappings never authorize collection of sources removed from `chats`.

## Other boundaries

- Company notices must also come from specified sources, not all company conversations.
- Attachments default to references. Read contents only when relevant and within the authorized scope.
- Timezone remains UTC+8. Frequency, allowed hours, working-day and holiday policies are not configured.
- Deadline reminders without new messages are not enabled.
- Do not adopt real sources, identities, dates, schedules, or historical task states from reference prompts.

Never copy real configuration into LOG, examples, or rules. The project ignores all `output/`; reports may be versioned in their independent local repository, which excludes attachments. Working files and state stay outside that repository.

Use `scripts/sync.py` for name resolution and manual collection. Record coverage only after actual successful reading and complete pagination. No scheduler is configured.
