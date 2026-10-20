#!/usr/bin/env python3
# 用途：将已采集的合并转发备份拆为逐条证据，并与原群核对；不调用飞书。
# 用法：python3 scripts/reconcile_backup.py --source '配置中的群名' --backup '配置中的同事姓名' --day 2026-10-20
# 无原消息 ID 的转发只记录时间、发送者与内容核对结果，不删除原记录、不恢复撤回内容。

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
from sync import ROOT, STATE, atomic, key, message_order, message_time, parse_time, read


def normalize(content):
    content = re.sub(r'(?:img|file)_[A-Za-z0-9_-]+', '<资源标识>', content)
    content = re.sub(r'@([^\s@()]+)\(\1\)', r'@\1', content)
    return '\n'.join(line.rstrip() for line in content.strip().splitlines())


def entries(content):
    if not content.startswith('<forwarded_messages>') or not content.rstrip().endswith('</forwarded_messages>'):
        raise ValueError('合并转发没有完整起止标签，不能按完整备份处理。')
    body = content[len('<forwarded_messages>'):].removesuffix('</forwarded_messages>').strip('\n')
    heads = list(re.finditer(r'^\[(\d{4}-\d{2}-\d{2}T[^\]\n]+)\] ([^\n]+):\n', body, re.M))
    if not heads or body[:heads[0].start()].strip():
        raise ValueError('合并转发内部格式不明确。')
    rows = []
    for i, match in enumerate(heads):
        block = body[match.end():heads[i+1].start() if i+1 < len(heads) else len(body)]
        text = '\n'.join(line[4:] if line.startswith('    ') else line for line in block.splitlines()).rstrip('\n')
        rows.append({'time': match.group(1), 'sender': match.group(2), 'content': text})
    return rows


def run(source_name, backup_name, day):
    mapping = read(STATE / 'chat-map.json', {})
    source = read(STATE / 'chats' / key(mapping[source_name]['chat_id']) / 'state.json')
    backup = read(STATE / 'chats' / key(mapping[backup_name]['chat_id']) / 'state.json')
    candidates = defaultdict(list)
    for row in source['messages'].values():
        m = row['message']
        if not m.get('deleted'):
            identity = (message_time(m).strftime('%Y-%m-%d %H:%M'), m.get('sender', {}).get('name'), normalize(m.get('content','')))
            candidates[identity].append(m)
    used = set()
    batches = []
    for row in sorted(backup['messages'].values(), key=lambda r:message_order(r['message'])):
        wrapper = row['message']
        if wrapper.get('msg_type') != 'merge_forward' or message_time(wrapper).strftime('%Y-%m-%d') != day:
            continue
        extracted = entries(wrapper['content'])
        for entry in extracted:
            identity = (parse_time(entry['time']).strftime('%Y-%m-%d %H:%M'), entry['sender'], normalize(entry['content']))
            matches = [m for m in candidates[identity] if m['message_id'] not in used]
            if len(matches) == 1:
                entry['matched_message_id'] = matches[0]['message_id']
                entry['match'] = '时间分钟、发送者、资源标识归一后的文本一致'
                used.add(matches[0]['message_id'])
            else:
                entry['match'] = '待核对' if not matches else '多条候选，待核对'
                entry['candidate_ids'] = [m['message_id'] for m in matches]
        batches.append({'wrapper_message_id': wrapper['message_id'], 'forwarded_at': wrapper['create_time'],
                       'source_link': wrapper.get('message_app_link'), 'count':len(extracted),
                       'matched':sum('matched_message_id' in e for e in extracted), 'entries':extracted})
    result = {'source':source_name,'backup':backup_name,'day':day,'batches':batches,
              'note':'转发不提供原消息 ID；匹配是文本核对结果，不等于 ID 级一致，不自动合并或删除记录。'}
    atomic(STATE / 'backup-reconciliation.json', result)
    return {'batches':[{'id':b['wrapper_message_id'],'count':b['count'],'matched':b['matched']} for b in batches]}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='本地合并转发备份核对')
    parser.add_argument('--source',required=True)
    parser.add_argument('--backup',required=True)
    parser.add_argument('--day',required=True)
    args=parser.parse_args()
    try:
        parse_time(args.day)
        print(json.dumps({'ok':True,**run(args.source,args.backup,args.day)},ensure_ascii=False,indent=2))
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(json.dumps({'ok':False,'error':str(error)},ensure_ascii=False),file=sys.stderr)
        sys.exit(1)
