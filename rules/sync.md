# Collection and monitoring

## Before calling Lark

Read AGENTS.md, config/sources.md, and config/sources.local.json. Real sources come only from the local JSON; missing or invalid configuration stops collection without using examples. Permit read-only queries only within confirmed sources and time ranges. Verify command effects: sending, remote writes, and remote configuration changes are forbidden. No listening method is selected; do not register subscriptions or start a persistent process automatically.

If time restrictions are adopted later, check them before every request, page, and retry. A policy skip is not a successful sync; advance no cursors and change no completion states. If Chinese working-day rules are confirmed, use official State Council notices. If the calendar is missing and cannot be verified, stop collection and notify once instead of substituting weekdays.

## Source resolution

The user maintains since and chats, with optional report_language. Follow config/sources.md to resolve configured names. Save unique, explicit matches in output/state/chat-map.json; wait for confirmation on duplicates or fuzzy matches. Query only necessary identifying information, not messages from unspecified sources, and perform no remote writes.

Every run is limited by the current chats list. Old mappings never expand scope. Initial collection starts at since, 00:00 UTC+8; later runs use the saved cursor.

## Incremental collection and recovery

scripts/sync.py performs manual collection under these constraints. Messages, cursors, and pending state live in output/state/; batches and working material in output/work/; final documents in output/reports/YYYYMMDD/<task-directory>/. The project ignores all output; the local report repository excludes attachments.

- Maintain per-chat successful cursors. Confirm initial dates, then overlap later runs by 10 minutes and deduplicate by message ID.
- Preserve source chat, message ID, speaker, message time, collection time, link or locator, and evidence of edits.
- The overlap cannot guarantee discovery of older edits or deletions. Do not claim coverage of changes that were not checked.
- Advance a cursor only after complete pagination and successful persistence. One source succeeding does not prove all sources succeeded.
- Keep collected but unanalyzed content pending. Process at most 100 messages per batch per source. Split long messages and retain unread portions.
- Keep collection and analysis progress separate. Remove analyzed pending entries only after saving related records and only if their versions remain unchanged.
- Write temporary files in the target data directory and atomically replace each destination. Do not assume multi-file atomicity; preserve recovery and idempotency and prevent concurrent overwrites.
- On failure, retain prior records and pending content. Explain affected sources, dates, and possible gaps. Backfill only within the authorized scope after recovery.

## Reading volume and output

Start with current-run results, pending messages, relevant current item states, and user feedback. Read targeted history only to verify context, not every accumulated chat or report.

Attachments default to references. If links are unavailable, retain message IDs without inventing links. Unread attachments are not verified evidence.

With no new messages, feedback, or state changes, do not repeat analysis or reminders. Reminders appear only in the current user interaction channel, never in Lark or to other people. Author reports and advice using report_language (default zh); preserve source material unchanged. Collection batches and diagnostics are internal material, not final reports.

## Manual execution and completeness

Perform each explicitly requested collection within its stated scope. Without an approved recurring policy, do not schedule another run. Scripts expose fixed read-only commands, not arbitrary APIs or CLI commands. Their allowlist constrains their own calls, not every CLI or computer permission.

Validate data.messages, has_more, and page_token; unknown response shapes stop collection rather than becoming empty results. Fully paginate thread replies separately. Thread APIs lack time filtering, so retain only authorized replies and do not persist returned out-of-range replies as business records. Record merged forwards and recalled messages as separate completeness issues; ordinary pagination success does not prove their contents are complete.

For complete discussion archives, follow “Two documents” in [records.md](records.md). Keep execution details in output/work/YYYYMMDD/<task-directory>/archive.md.
