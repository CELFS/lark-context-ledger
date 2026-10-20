#!/usr/bin/env python3
# Purpose: build one chronological transcript and one daily summary from collected messages and a reviewed index.
# Usage (from the repository root): python3 scripts/build_document.py 'output/work/YYYYMMDD/task-directory/topic-index.json'
# See rules/records.md for index format and review rules; local files only, with no Lark or AI API calls.

import argparse
from datetime import datetime
import json
import os
import re
from pathlib import Path
import sys

sys.dont_write_bytecode = True

from sync import ROOT, STATE, atomic, key, message_time, message_order, parse_time, report_language


# Localize generated labels only; never automatically translate messages, quotations, or the reviewed summary draft.
REPORT_TEXT = {
    'zh': {
        'transcript': '原稿', 'range': '范围：{start} 至 {end}（北京时间）。',
        'sources': '来源：{sources}。', 'source_separator': '、',
        'note': '按时间顺序保留消息，每条仅出现一次。时间按原消息可见精度显示；正文为采集时可见版本。附件本地保存，未纳入 Git，正文不重复嵌入附件全文。',
        'summary': '阅读整理稿',
        'deleted_count': '本范围有 {count} 条撤回消息无法恢复正文，按原位置标记。',
        'gaps': '其他缺口：', 'gap_separator': '；',
        'unknown_sender': '发送者未返回', 'previous': '此前消息', 'reply': '回复：',
        'outside_reply': '回复此前消息（不在本次采集范围内）。',
        'deleted': '此条消息已撤回，原文无法恢复。',
        'screenshot': '原始截图', 'attachment': '附件：',
    },
    'en': {
        'transcript': 'Transcript', 'range': 'Range: {start} to {end} (UTC+8).',
        'sources': 'Sources: {sources}.', 'source_separator': ', ',
        'note': 'Messages appear once in chronological order, with the timestamp precision and text visible when collected. Attachments are stored locally, excluded from Git, and linked without duplicating their full contents.',
        'summary': 'Read summary',
        'deleted_count': '{count} recalled messages cannot be recovered; their original positions are marked.',
        'gaps': 'Other gaps: ', 'gap_separator': '; ',
        'unknown_sender': 'Sender unavailable', 'previous': 'Earlier message', 'reply': 'Reply to: ',
        'outside_reply': 'Reply to an earlier message outside this collection range.',
        'deleted': 'This message was recalled; its original text cannot be recovered.',
        'screenshot': 'Original screenshot', 'attachment': 'Attachment: ',
    },
}


def inside_output(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to((ROOT / 'output').resolve()):
        raise ValueError('文档输入输出路径必须位于 output/ 内。')
    return path


def text(message):
    content = message.get('content', '')
    return content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, indent=2)


def build(manifest):
    language = report_language()
    labels = REPORT_TEXT[language]
    start, end = parse_time(manifest['start']), parse_time(manifest['end'])
    if end <= start:
        raise ValueError('索引时间范围无效。')
    mapping = json.loads((STATE / 'chat-map.json').read_text(encoding='utf-8'))
    pool = {}
    gaps = []
    sources = []
    for name in manifest['chats']:
        target = mapping[name]
        book = json.loads((STATE / 'chats' / key(target['chat_id']) / 'state.json').read_text(encoding='utf-8'))
        intervals = sorted((parse_time(c['start']), parse_time(c['end'])) for c in book['coverage']
                           if c.get('messages_paginated'))
        covered = start
        for left, right in intervals:
            if left <= covered:
                covered = max(covered, right)
        if covered < end:
            raise ValueError(name + ' 未完整分页覆盖索引时间范围，不能生成完整归档。')
        sources.append(target.get('name', name))
        for mid, row in book['messages'].items():
            if start <= message_time(row['message']) <= end:
                if mid in pool and pool[mid]['message'] != row['message']:
                    raise ValueError('同一消息 ID 的两个来源内容冲突，需先核对。')
                pool[mid] = dict(row, source_name=target.get('name', name), chat_id=target['chat_id'])
        gaps += [dict(g, source=name) for g in book.get('gaps', []) if g.get('message_id') in pool]
    resources = []
    if manifest.get('resource_index'):
        resources = json.loads(inside_output(manifest['resource_index']).read_text(encoding='utf-8'))
        for resource in resources:
            if resource.get('ok') and not inside_output(resource['path']).is_file():
                raise ValueError('已登记附件不存在：' + resource['path'])
    by_message = {}
    for resource in resources:
        if resource.get('ok') and resource['message_id'] in pool:
            by_message.setdefault(resource['message_id'], []).append(resource)
    destination = inside_output(manifest['output'])
    def relative(value):
        return os.path.relpath(inside_output(value), destination.parent)
    # Preserve recorded collection gaps; omit resolved attachment gaps from the transcript after successful download.
    unresolved = []
    for gap in gaps:
        if gap['message_id'] in by_message and ('附件' in gap['reason'] or '富文本' in gap['reason']):
            continue
        unresolved.append(gap)
    gaps = unresolved
    topics = manifest['topics']
    if not topics or len({t['title'] for t in topics}) != len(topics):
        raise ValueError('必须有非空且标题不重复的话题。')
    used = set()
    for topic in topics:
        if not topic.get('title', '').strip() or not topic.get('message_ids'):
            raise ValueError('每个话题须有标题和原文消息 ID。')
        for mid in topic['message_ids']:
            if mid not in pool:
                raise ValueError('话题引用了范围外或未采集的消息：' + mid)
            used.add(mid)
    excluded = manifest.get('excluded', {})
    if not isinstance(excluded, dict) or any(not isinstance(reason, str) or not reason.strip() for reason in excluded.values()):
        raise ValueError('排除项须按消息 ID 记录明确理由。')
    if set(excluded) - pool.keys() or used & excluded.keys():
        raise ValueError('排除项不存在或与话题引用冲突。')
    missing = pool.keys() - used - excluded.keys()
    if missing:
        raise ValueError('仍有未分类消息，不能直接遗漏：' + ', '.join(sorted(missing)[:10]))
    deleted_ids = {mid for mid, row in pool.items() if row['message'].get('deleted')}
    gaps = [g for g in gaps if g['message_id'] in used and (g['message_id'] not in deleted_ids or '已撤回' in g['reason'])]
    summary_destination = inside_output(manifest['summary_output'])
    if destination.parent != summary_destination.parent or destination == summary_destination:
        raise ValueError('原稿和整理稿须为同一任务目录下的不同文件。')
    reading = inside_output(manifest['reading_draft']).read_text(encoding='utf-8').strip()
    if not reading:
        raise ValueError('请先完成整理稿，不能仅交付内部索引。')
    lines = ['# ' + manifest['title'] + ' · ' + labels['transcript'], '',
             labels['range'].format(start=start.strftime('%Y-%m-%d %H:%M'), end=end.strftime('%Y-%m-%d %H:%M')),
             labels['sources'].format(sources=labels['source_separator'].join(sources)), '',
             labels['note'], '',
             '[' + labels['summary'] + '](' + summary_destination.name + ')', '']
    if gaps:
        deleted_count = len({g['message_id'] for g in gaps if '已撤回' in g['reason']})
        if deleted_count:
            lines += [labels['deleted_count'].format(count=deleted_count), '']
        other = [g for g in gaps if '已撤回' not in g['reason']]
        if other:
            lines += [labels['gaps'] + labels['gap_separator'].join(dict.fromkeys(g['reason'] for g in other)), '']
    rows = sorted(pool.values(), key=lambda row: message_order(row['message']))
    for row in rows:
        m = row['message']
        mid = m['message_id']
        sender = str(m.get('sender', {}).get('name') or labels['unknown_sender'])
        label = message_time(m).strftime('%m-%d %H:%M') + ' · ' + sender
        if m.get('message_app_link'):
            label = '[' + label + '](' + m['message_app_link'] + ')'
        lines += ['<a id="' + mid + '"></a> **' + label + '**']
        parent = m.get('reply_to')
        if isinstance(parent, dict):
            parent = parent.get('message_id')
        if parent:
            if parent in pool:
                previous = pool[parent]['message']
                parent_label = str(previous.get('sender', {}).get('name') or labels['previous']) + ' ' + message_time(previous).strftime('%m-%d %H:%M')
                lines += [labels['reply'] + '[' + parent_label + '](#' + parent + ')', '']
            else:
                lines += [labels['outside_reply'], '']
        if m.get('deleted'):
            lines += [labels['deleted'], '']
            continue
        body = text(m)
        fence = '`' * max(4, max((len(v) for v in re.findall(r'`{3,}', body)), default=3) + 1)
        lines += [fence + 'text', body, fence, '']
        for resource in by_message.get(mid, []):
            filename = re.search(r'name="([^\"]+)"', body)
            resource_label = filename.group(1) if resource['type'] == 'file' and filename else labels['screenshot']
            lines += [labels['attachment'] + '[' + resource_label + '](' + relative(resource['path']) + ')', '']
    # Use IDs only for hidden anchors and reference validation, not as visible fields in the reading text.
    for target in re.findall(re.escape(destination.name) + r'#([^\)]+)', reading):
        if target not in pool:
            raise ValueError('整理稿引用的原消息不存在：' + target)
    atomic(destination, '\n'.join(lines))
    atomic(summary_destination, reading + '\n')
    return {'original': str(destination.relative_to(ROOT)), 'summary': str(summary_destination.relative_to(ROOT)),
            'messages': len(pool), 'content_gaps': gaps, 'report_language': language}



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='保存单份时间顺序原稿与日常整理稿。')
    parser.add_argument('manifest', help='output/ 内的话题索引 JSON')
    args = parser.parse_args()
    try:
        manifest = json.loads(inside_output(args.manifest).read_text(encoding='utf-8'))
        print(json.dumps({'ok': True, **build(manifest)}, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
