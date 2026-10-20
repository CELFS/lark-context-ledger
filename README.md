# work-context

采集工作沟通，整理任务与背景，回顾沟通方式，提前发现口径缺口。飞书严格只读，AI 不发送消息、不修改业务数据。

## 日常使用

在本地配置填写起始日期与聊天名称，然后在对话中提出需求，例如“整理指定群最近的讨论”“更新任务进展”“回顾这段沟通”。

每个任务只需看两份文档：

```text
output/
  tasks/<任务ID>/
    YYYYMMDD-主题-整理稿.md      日常阅读：背景、结论、变化和待办
    YYYYMMDD-主题-原文归档.md    查证：说话人、时间、正文和回复关联
    attachments/       原附件，本地保留，Git 忽略
  work/                过程材料，Git 忽略
  state/               同步状态，Git 忽略
```

文件名使用整理日期（YYYYMMDD）、来源或具体主题、文档类型，避免只用“整理稿”或“原文归档”。正文保留覆盖的消息时间范围。原文每条只保存一次，附件不重复嵌入全文。后续默认先读整理稿，再按需追溯原文；已有资料复用，增量更新。

README 仅说明用途与用法；具体需求和结果全部在 output/。根 LOG.md 只记录不含具体业务内容的维护或运行日志。

## 配置与命令

真实配置使用 `config/sources.local.json`，已 Git 忽略；格式见 [配置说明](config/sources.md) 和 [示例](config/sources.example.json)。只需填写 since 与 chats，名称定位由工具处理，重名先确认。

以下命令在仓库根目录执行，使用 Python 标准库和已授权的飞书 CLI：

```bash
python3 scripts/sync.py status
python3 scripts/sync.py collect --chat '配置中的名称'
python3 scripts/sync.py export --chat '配置中的名称'
python3 scripts/build_document.py output/work/任务ID/topic-index.json
```

名称定位使用 sync.py resolve，备份核对使用 reconcile_backup.py --source '群名' --backup '姓名' --day YYYY-MM-DD。未启用定时运行；脚本负责采集与保存，AI 负责理解和整理。

## 规则入口

[总边界](AGENTS.md) · [本地技能](.agents/skills/work-context/SKILL.md) · [采集规则](rules/sync.md) · [记录规则](rules/records.md) · [沟通回顾](rules/communication.md) · [日志](LOG.md)
