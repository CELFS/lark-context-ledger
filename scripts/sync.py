#!/usr/bin/env python3
# Purpose: resolve configured chats, paginate collection, and save local state using fixed read-only Lark CLI commands.
# Usage (from the repository root):
#   python3 scripts/sync.py status
#   python3 scripts/sync.py resolve --chat 'Configured chat name'
#   python3 scripts/sync.py collect --chat 'Configured chat name'
#   python3 scripts/sync.py collect --chat 'Configured chat name' --start '2026-10-20T11:00:00+08:00'
#   python3 scripts/sync.py export --chat 'Configured chat name'
# No messages, remote mutations, automatic login, or scheduling; Python standard library only.

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'output/state'
TZ = timezone(timedelta(hours=8))
ALLOWED = {
    ('im', '+chat-search'), ('contact', '+search-user'),
    ('im', '+chat-messages-list'), ('im', '+threads-messages-list'),
    ('im', '+messages-mget'),
}


def now():
    return datetime.now(TZ).isoformat(timespec='seconds')


def read(path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    fd, name = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def lock():
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE / '.sync.lock').open('a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('另一个采集进程正在运行，请稍后重试。')
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def config():
    data = read(ROOT / 'config/sources.local.json')
    if not isinstance(data, dict) or not isinstance(data.get('chats'), list):
        raise ValueError('本地监听配置缺失或无效。')
    if any(not isinstance(s, str) or not s.strip() or s != s.strip() for s in data['chats']):
        raise ValueError('聊天名称须为非空字符串，且不含首尾空格。')
    if len(set(data['chats'])) != len(data['chats']):
        raise ValueError('配置中有重复聊天名称。')
    parse_time(data.get('since', ''))
    report_language(data)
    return data


def report_language(data=None):
    if data is None:
        data = read(ROOT / 'config/sources.local.json', {})
    if not isinstance(data, dict):
        raise ValueError('本地配置须为 JSON 对象。')
    language = data.get('report_language', 'zh')
    if not isinstance(language, str) or language not in ('zh', 'en'):
        raise ValueError('report_language 仅支持 zh 或 en；省略时默认 zh。')
    return language


def parse_time(value):
    if not isinstance(value, str) or not value:
        raise ValueError('请填写起始日期 since。')
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        return datetime.strptime(value, '%Y-%m-%d').replace(tzinfo=TZ)
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('日期时间必须带时区；日期可使用 YYYY-MM-DD。')
    return parsed.astimezone(TZ)


def key(value):
    return hashlib.sha256(value.encode()).hexdigest()[:20]


def cli(command, args):
    if tuple(command) not in ALLOWED:
        raise ValueError('拒绝调用不在只读白名单中的命令。')
    env = dict(os.environ, LARKSUITE_CLI_NO_UPDATE_NOTIFIER='1', LARKSUITE_CLI_NO_SKILLS_NOTIFIER='1')
    result = subprocess.run(['lark-cli', *command, *args, '--as', 'user', '--format', 'json'],
                            cwd=ROOT, env=env, text=True, capture_output=True, timeout=120)
    try:
        envelope = json.loads(result.stdout if result.returncode == 0 else result.stderr)
    except json.JSONDecodeError:
        raise ValueError('CLI 未返回有效 JSON，未推进进度；请单独检查 CLI 配置。')
    if result.returncode or envelope.get('ok') is not True:
        error = envelope.get('error', {})
        missing = error.get('missing_scopes', [])
        if missing and isinstance(missing, list):
            raise ValueError('缺少只读权限：' + ', '.join(str(v) for v in missing) + '；需用户完成对应授权。')
        # Do not print raw command output, which may expose authentication details in reports.
        raise ValueError('飞书只读请求失败：' + str(error.get('type', 'unknown')) + '/' +
                         str(error.get('subtype', 'unknown')) + '；请核实配置和只读权限。')
    if not isinstance(envelope.get('data'), dict):
        raise ValueError('CLI data 结构未知，停止并保留已有数据。')
    return envelope


def pages(command, args, field):
    token = None
    seen = set()
    while True:
        response = cli(command, [*args, *(['--page-token', token] if token else [])])
        data = response['data']
        items = data.get(field)
        pagination = response.get('meta', {}).get('pagination', {})
        # The CLI returns chats as null for an explicit empty search result.
        if field in data and items is None and data.get('has_more') is False and pagination.get('complete') is True and pagination.get('items') == 0:
            items = []
        if not isinstance(items, list):
            raise ValueError('CLI 缺少 ' + field + ' 数组，停止，不将其视为空结果。')
        yield response, items
        more = data.get('has_more')
        if not isinstance(more, bool):
            raise ValueError('CLI 缺少明确的 has_more 分页状态，不能证明分页完整。')
        if not more:
            return
        token = data.get('page_token')
        if not isinstance(token, str) or not token or token in seen:
            raise ValueError('分页游标缺失或重复，未推进同步位置。')
        seen.add(token)


def resolve(name, mapping, chosen=None):
    if name in mapping and chosen is None:
        return mapping[name]
    groups = []
    for _, rows in pages(('im', '+chat-search'),
                         ['--query', name, '--disable-search-by-user', '--page-size', '100'], 'chats'):
        groups.extend({'name': row.get('name'), 'kind': 'group', 'chat_id': row.get('chat_id')}
                      for row in rows if row.get('chat_id'))
    response = cli(('contact', '+search-user'), ['--query', name, '--has-chatted', '--page-size', '30'])
    users = response['data']
    if not isinstance(users.get('users'), list) or users.get('has_more') is not False:
        raise ValueError('联系人结果不完整，需要缩小名称范围。')
    candidates = groups + [
        {'name': row.get('localized_name'), 'kind': 'private', 'chat_id': row.get('p2p_chat_id')}
        for row in users['users'] if row.get('p2p_chat_id')
    ]
    candidates = list({row['chat_id']: row for row in candidates}.values())
    exact = [row for row in candidates if row['name'] == name]
    if chosen:
        exact = [row for row in candidates if row['chat_id'] == chosen]
    if len(exact) != 1:
        atomic(STATE / ('candidates-' + key(name) + '.json'), {'query': name, 'candidates': candidates})
        raise ValueError('名称未唯一明确匹配。请查看 output/state/candidates-' + key(name) +
                         '.json，由用户确认后用 resolve --select 候选ID；未读取消息。')
    selected = dict(exact[0], query=name, resolved_at=now())
    mapping[name] = selected
    atomic(STATE / 'chat-map.json', mapping)
    return selected


def message_time(message):
    value = message.get('create_time')
    try:
        number = float(value)
        if number > 100000000000:
            number /= 1000
        return datetime.fromtimestamp(number, TZ)
    except (TypeError, ValueError, OverflowError, OSError):
        # The CLI returns minute-precision UTC+8 strings rather than consistent millisecond timestamps.
        if isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?::\d{2})?', value):
            return datetime.fromisoformat(value).replace(tzinfo=TZ)
        return parse_time(value)


def message_order(message):
    position = str(message.get('message_position', ''))
    return (message_time(message), int(position) if position.isdigit() else 10**20)


def fingerprint(message):
    return hashlib.sha256(json.dumps(message, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def store_messages(book, messages, source):
    for message in messages:
        if not isinstance(message, dict) or not message.get('message_id'):
            raise ValueError('消息缺少稳定 ID，保留响应，但停止推进进度。')
        mid = message['message_id']
        previous = book['messages'].get(mid)
        digest = fingerprint(message)
        if previous is None or previous['fingerprint'] != digest:
            if previous:
                book.setdefault('versions', {}).setdefault(mid, []).append(previous)
            book['messages'][mid] = {'fingerprint': digest, 'captured_at': now(),
                                      'origin': source, 'message': message}
            book.setdefault('pending', {})[mid] = digest
        for field in ('thread_replies',):
            replies = message.get(field, [])
            if isinstance(replies, list):
                store_messages(book, replies, 'embedded-thread')
            elif replies:
                book.setdefault('gaps', []).append({'message_id': mid, 'reason': '未知内嵌回复结构'})


def collect(name, mapping, cfg, args):
    target = resolve(name, mapping)
    cid = target['chat_id']
    folder = STATE / 'chats' / key(cid)
    path = folder / 'state.json'
    book = read(path, {'messages': {}, 'versions': {}, 'pending': {}, 'cursor': None, 'coverage': []})
    first = parse_time(cfg['since'])
    start = parse_time(args.start) if args.start else (
        max(first, parse_time(book['cursor']) - timedelta(minutes=10)) if book['cursor'] else first)
    end = parse_time(args.end) if args.end else datetime.now(TZ)
    if start < first or end <= start or end > datetime.now(TZ) + timedelta(seconds=5):
        raise ValueError('时间范围无效，不能早于配置起点或晚于当前时间。')
    run = datetime.now(TZ).strftime('%Y%m%dT%H%M%S%f')
    count = 0
    book['source'] = target
    book['last_attempt'] = {'start': start.isoformat(), 'end': end.isoformat(), 'complete': False}
    atomic(path, book)
    try:
        params = ['--chat-id', cid, '--start', start.isoformat(), '--end', end.isoformat(),
                  '--order', 'asc', '--page-size', '50', '--no-reactions']
        for index, (response, messages) in enumerate(pages(('im', '+chat-messages-list'), params, 'messages'), 1):
            atomic(folder / 'responses' / run / ('page-' + str(index) + '.json'), response)
            store_messages(book, messages, 'chat-history')
            count += len(messages)
            atomic(path, book)
        threads = sorted({row['message'].get('thread_id') for row in book['messages'].values()
                          if row['message'].get('thread_id')})
        thread_coverage = []
        for thread in threads:
            # Thread APIs lack time filtering; save only authorized messages and do not persist the raw response.
            for _, messages in pages(('im', '+threads-messages-list'),
                                     ['--thread', thread, '--order', 'asc', '--page-size', '50', '--no-reactions'], 'messages'):
                filtered = [m for m in messages if first <= message_time(m) <= end]
                store_messages(book, filtered, 'thread-history')
                atomic(path, book)
            thread_coverage.append(thread)
        gaps = []
        for mid, row in book['messages'].items():
            message = row['message']
            if message.get('deleted'):
                gaps.append({'message_id': mid, 'reason': '已撤回，不能证明原文可恢复'})
            if message.get('msg_type') in {'image', 'file', 'audio', 'video', 'media', 'interactive', 'folder'}:
                gaps.append({'message_id': mid, 'reason': '附件或卡片仅保留 CLI 返回的引用／文本，尚未核实其完整内容'})
            if message.get('msg_type') == 'post' and re.search(r'!\[|<(?:file|folder|audio|video)\b', str(message.get('content', ''))):
                gaps.append({'message_id': mid, 'reason': '富文本含附件引用，附件正文尚未读取'})
            if message.get('msg_type') == 'merge_forward':
                gaps.append({'message_id': mid, 'reason': '合并转发需逐项核对内部消息和原始时间；不能以外层摘要证明完整'})
        book['gaps'] = gaps
        book['coverage'].append({'start': start.isoformat(), 'end': end.isoformat(),
                                 'messages_paginated': True, 'threads_checked': thread_coverage})
        # Explicit backfills add evidence without advancing across an uncollected gap after the existing cursor.
        baseline = parse_time(book['cursor']) if book['cursor'] else first
        if start <= baseline:
            book['cursor'] = max(baseline, end).isoformat()
        book['last_attempt']['complete'] = True
        book['last_attempt']['fetched_top_level'] = count
        atomic(path, book)
    except Exception:
        atomic(path, book)
        raise
    return {'name': name, 'stored_messages': len(book['messages']), 'pending': len(book['pending']),
            'start': start.isoformat(), 'end': end.isoformat(), 'pagination_complete': True,
            'content_gaps': len(book['gaps']), 'cursor': book['cursor']}


def export(name, mapping):
    if name not in mapping:
        raise ValueError('尚未定位该聊天。')
    cid = mapping[name]['chat_id']
    book = read(STATE / 'chats' / key(cid) / 'state.json')
    if not book:
        raise ValueError('该来源还没有采集记录。')
    rows = sorted(book['messages'].values(), key=lambda row: message_order(row['message']))
    destination = ROOT / 'output/work/sources' / key(cid)
    files = []
    for offset in range(0, len(rows), 100):
        batch = rows[offset:offset + 100]
        lines = ['# ' + name + ' — 原文批次 ' + str(offset // 100 + 1), '',
                 '内容为 CLI 返回的消息文本；时间按 CLI 的北京时间解释，可能仅精确到分钟；附件、卡片和合并转发不能据此视为已读全文。', '']
        for row in batch:
            m = row['message']
            sender = m.get('sender', {})
            sender_name = sender.get('name') or sender.get('id') or '发送者未返回'
            lines += ['## ' + m['message_id'], '', '- 时间：' + message_time(m).isoformat(),
                      '- 发送者：' + str(sender_name), '- 类型：' + str(m.get('msg_type', '未知')),
                      '- 会话 ID：' + cid]
            link = m.get('message_app_link')
            if link:
                lines.append('- 消息链接：' + link)
            content = m.get('content', '')
            if not isinstance(content, str):
                content = json.dumps(content, ensure_ascii=False, indent=2)
            # Quote every line so external content cannot change the document section structure.
            lines += ['', *['> ' + line for line in content.split('\n')], '']
        file = destination / ('batch-' + str(offset // 100 + 1).zfill(4) + '.md')
        atomic(file, '\n'.join(lines))
        files.append(str(file.relative_to(ROOT)))
    atomic(destination / 'index.json', {'source': name, 'message_count': len(rows), 'batches': files,
                                        'coverage': book['coverage'], 'gaps': book.get('gaps', [])})
    return {'name': name, 'message_count': len(rows), 'batches': files, 'gaps': book.get('gaps', [])}


def main():
    parser = argparse.ArgumentParser(description='飞书指定来源只读采集；不会发送消息或写入远端。')
    parser.add_argument('action', choices=['status', 'resolve', 'collect', 'export'])
    parser.add_argument('--chat', action='append', help='仅处理已配置名称，可重复；不传时处理全部配置来源')
    parser.add_argument('--select', help='resolve 重名候选，由用户明确确认的会话 ID')
    parser.add_argument('--start', help='collect 显式补采起点，带时区；不自动重置连续同步位置')
    parser.add_argument('--end', help='collect 截止时间，带时区；默认本轮开始时间')
    args = parser.parse_args()
    cfg = config()
    names = args.chat if args.chat else cfg['chats']
    if len(set(names)) != len(names) or any(name not in cfg['chats'] for name in names):
        raise ValueError('仅可处理当前配置中的唯一聊天名称。')
    if args.select and (args.action != 'resolve' or len(names) != 1):
        raise ValueError('--select 仅用于一个已由用户确认的 resolve 来源。')
    with lock():
        mapping = read(STATE / 'chat-map.json', {})
        results = []
        for name in names:
            try:
                if args.action == 'status':
                    target = mapping.get(name)
                    book = read(STATE / 'chats' / key(target['chat_id']) / 'state.json', {}) if target else {}
                    result = {'name': name, 'resolved': bool(target), 'cursor': book.get('cursor'),
                              'messages': len(book.get('messages', {})), 'pending': len(book.get('pending', {})),
                              'last_attempt': book.get('last_attempt')}
                elif args.action == 'resolve':
                    result = resolve(name, mapping, args.select)
                elif args.action == 'collect':
                    result = collect(name, mapping, cfg, args)
                else:
                    result = export(name, mapping)
                results.append({'ok': True, 'result': result})
            except (ValueError, OSError, subprocess.TimeoutExpired) as error:
                results.append({'ok': False, 'name': name, 'error': str(error)})
        if args.action != 'status':
            atomic(STATE / 'last-run.json', {'action': args.action, 'time': now(), 'results': results})
        print(json.dumps({'ok': all(row['ok'] for row in results), 'results': results}, ensure_ascii=False, indent=2))
        return 0 if all(row['ok'] for row in results) else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
