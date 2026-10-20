#!/usr/bin/env python3
# 用途：基于已采集消息和 AI 审阅后的话题索引生成“分话题原文 + 独立整理章节”。
# 用法（在仓库根目录）：python3 scripts/build_document.py output/state/<话题索引>.json
# 索引格式和人工核对规则见 rules/records.md；只读取本地文件，不调用飞书或 AI API。

import argparse
from datetime import datetime
import json
import os
import re
from pathlib import Path
import sys

sys.dont_write_bytecode = True

from sync import ROOT, STATE, atomic, key, message_time, message_order, parse_time


def inside_output(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to((ROOT / 'output').resolve()):
        raise ValueError('文档输入输出路径必须位于 output/ 内。')
    return path


def text(message):
    content = message.get('content', '')
    return content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, indent=2)


def build(manifest):
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
    # 采集时记录的附件缺口，下载成功后仍保留原记录，但在归档中显示已归档状态。
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
    summaries = []
    for topic in topics:
        if not topic.get('title', '').strip() or not topic.get('message_ids'):
            raise ValueError('每个话题须有标题和原文消息 ID。')
        for mid in topic['message_ids']:
            if mid not in pool:
                raise ValueError('话题引用了范围外或未采集的消息：' + mid)
            used.add(mid)
        summary_path = inside_output(topic['summary'])
        summary = summary_path.read_text(encoding='utf-8').strip()
        if not summary:
            raise ValueError('话题整理章节尚未完成。')
        summaries.append(summary)
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
    lines = ['# ' + manifest['title'], '',
             '- 整理范围：' + start.isoformat() + ' 至 ' + end.isoformat(),
             '- 来源：' + '、'.join(sources),
             '- 已审阅消息：' + str(len(pool)) + '；话题引用：' + str(len(used)) + '；排除：' + str(len(excluded)),
             '- 本文原文为 CLI 返回的文本；编辑消息只代表采集时版本，附件正文不自动包含。', '']
    lines += ['## 目录', '', '- [采集核对与阅读说明](#archive-intro)', '- [一、按话题归档的原文](#archive-original)', '- [二、独立的话题整理](#archive-summary)', '- [三、跨话题进展与待确认](#archive-review)', '- [四、原始 Markdown 附件全文](#archive-attachments)', '- [五、排除记录](#archive-excluded)', '']
    if manifest.get('intro'):
        lines += ['<a id="archive-intro"></a>', '']
        lines += ['## 采集核对与阅读说明', '', inside_output(manifest['intro']).read_text(encoding='utf-8').strip(), '']
    if gaps:
        lines += ['## 完整性限制', '']
        for gap in gaps:
            lines.append('- ' + gap['source'] + ' / ' + gap['message_id'] + '：' + gap['reason'])
        lines.append('')
    lines += ['<a id="archive-original"></a>', '', '## 一、按话题归档的原文', '']
    anchored = set()
    for topic in topics:
        lines += ['### ' + topic['title'], '']
        selected = sorted((row for mid, row in pool.items() if mid in topic['message_ids']),
                          key=lambda row: message_order(row['message']))
        for row in selected:
            m = row['message']
            sender = m.get('sender', {})
            if m['message_id'] not in anchored:
                lines += ['<a id="' + m['message_id'] + '"></a>', '']
                anchored.add(m['message_id'])
            lines += ['#### ' + message_time(m).isoformat() + ' · ' + str(sender.get('name') or sender.get('id') or '发送者未返回'), '',
                      '- 来源：' + row['source_name'] + '；消息 ID：' + m['message_id'],
                      '- 消息类型：' + str(m.get('msg_type', '未知'))]
            if m.get('deleted'):
                lines.append('- 状态：已撤回；CLI 返回的 Invalid 标记不是可恢复的原文正文。')
            if m.get('updated'):
                lines.append('- 版本：消息曾编辑，以下为本次采集到的版本。')
            if m.get('reply_to'):
                lines.append('- 回复关系：' + json.dumps(m['reply_to'], ensure_ascii=False))
            if m.get('thread_id'):
                lines.append('- 话题 ID：' + m['thread_id'])
            if m.get('message_app_link'):
                lines.append('- 链接：' + m['message_app_link'])
            body = text(m)
            fence = '`' * max(4, max((len(v) for v in re.findall(r'`{3,}', body)), default=3) + 1)
            lines += ['', fence + 'text', body, fence, '']
            for resource in by_message.get(m['message_id'], []):
                label = resource['key']
                if resource['type'] == 'image':
                    lines += ['![原始截图 ' + m['message_id'] + '](' + relative(resource['path']) + ')', '']
                else:
                    lines += ['[下载的原附件](' + relative(resource['path']) + ')；全文见本文附件章节。', '']
    lines += ['<a id="archive-summary"></a>', '', '## 二、独立的话题整理', '']
    for topic, summary in zip(topics, summaries):
        lines += ['### ' + topic['title'], '', summary, '']
    if manifest.get('review'):
        lines += ['<a id="archive-review"></a>', '', '## 三、跨话题进展与待确认', '', inside_output(manifest['review']).read_text(encoding='utf-8').strip(), '']
    if manifest.get('include_attachments'):
        lines += ['<a id="archive-attachments"></a>', '', '## 四、原始 Markdown 附件全文', '', '附件按发送时版本原样保存；其中的路径、接口和实现声明属于当时文档，不自动视为当前已实现状态。原文中的本地相对路径保留在代码块内，引用时请结合来源仓库。', '']
        for resource in resources:
            if resource.get('ok') and resource['type'] == 'file' and resource['message_id'] in pool and resource['message_id'] in used:
                body = inside_output(resource['path']).read_text(encoding='utf-8')
                fences = [len(v) for v in re.findall(r'`{3,}', body)]
                fence = '`' * max(4, max(fences, default=3) + 1)
                m = pool[resource['message_id']]['message']
                filename = re.search(r'name="([^"]+)"', m['content'])
                label = filename.group(1) if filename else resource['message_id']
                lines += ['### ' + m['create_time'] + ' · ' + label, '', '- 消息 ID：' + resource['message_id'], '', fence + 'markdown', body, fence, '']
    lines += ['<a id="archive-excluded"></a>', '', '## 五、排除记录', '']
    for mid, reason in excluded.items():
        lines.append('- ' + mid + '：' + reason)
    if not excluded:
        lines.append('本次没有排除消息。')
    destination = inside_output(manifest['output'])
    atomic(destination, '\n'.join(lines))
    return {'document': str(destination.relative_to(ROOT)), 'messages': len(pool),
            'topic_messages': len(used), 'excluded': len(excluded), 'content_gaps': gaps}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='按话题保留消息原文，并拼接经审阅的独立整理章节。')
    parser.add_argument('manifest', help='output/ 内的话题索引 JSON')
    args = parser.parse_args()
    try:
        manifest = json.loads(inside_output(args.manifest).read_text(encoding='utf-8'))
        print(json.dumps({'ok': True, **build(manifest)}, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
