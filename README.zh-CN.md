# lark-context-ledger

[English](README.md) | 简体中文

基于 Lark CLI 采集工作沟通，整理任务与背景，回顾沟通方式，提前发现口径缺口。飞书严格只读，AI 不发送消息、不修改业务数据。

## 日常使用

在本地配置填写起始日期与聊天名称，然后在对话中提出需求，例如“整理指定群最近的讨论”“更新任务进展”“回顾这段沟通”。

需要保留个人思考时，明确要求保存为 `thinking`，用于回看讨论和自我提醒原则。普通聊天不会自动保存个人立场，也不代表授权采集飞书。

会话任务提供两份文档；thinking 使用一份带日期的 Markdown 笔记：

```text
output/
  reports/YYYYMMDD/
    NN-topic-MMDD_HHmm-MMDD_HHmm-主题-来源/
      YYYYMMDD-主题-整理稿.md      日常阅读：背景、结论、变化和待办
      YYYYMMDD-主题-原文归档.md    查证：说话人、时间、正文和回复关联
      attachments/               原附件，本地保留，Git 忽略
    NN-watch-MMDD_HHmm-主题-来源/  持续监听，仅标起始时间；文档结构同上
    NN-thinking-主题/
      YYYYMMDD-主题.md            个人思考：提醒原则、讨论整理和来源链接
  work/                过程材料，Git 忽略
  state/               同步状态，Git 忽略
```

目录按创建日期归档，NN 为三种类型共用的当天创建顺序，依次追加且不重排。`topic` 表示主题整理，包含消息起止时间；`watch` 表示持续监听，仅含消息起始时间；`thinking` 表示个人思考，不要求消息时间范围或聊天来源。会话后续更新沿用原目录，最新覆盖时间写在正文中；同一篇 thinking 的后续更新也沿用原目录。目录时间统一使用北京时间。命名为 watch 不代表已经启用监听。过程材料按相同日期和任务目录放入 `output/work/`。

会话任务的文件名使用整理日期（YYYYMMDD）、来源或具体主题、文档类型，避免只用“整理稿”或“原文归档”。正文保留覆盖的消息时间范围。原文每条只保存一次，附件不重复嵌入全文。后续默认先读整理稿，再按需追溯原文；已有资料复用，增量更新。

thinking 通过链接关联相关 topic 和已有证据，不重复复制原文。笔记中的原则属于个人思考，不自动变成项目规则、长期偏好或任务。直接保存 Markdown 笔记即可，不要求运行会话采集脚本或两份文档生成器。

README 仅说明用途与用法；具体需求和结果全部在 output/。根 LOG.md 只记录不含具体业务内容的维护或运行日志。

项目仓库忽略整个 `output/`。`output/reports/` 用于独立的本地 Git 仓库，保存报告版本；附件由其内部 `.gitignore` 忽略，过程材料和同步状态不纳入报告仓库。独立仓库由用户手动初始化和提交，不配置远程地址。

## 配置与命令

真实配置使用 `config/sources.local.json`，已 Git 忽略；格式见 [配置说明](config/sources.md) 和 [示例](config/sources.example.json)。必填 since 与 chats；可选 report_language，默认 zh，支持 zh/en。名称定位由工具处理，重名先确认。

报告语言由本地 JSON 的 `report_language` 控制：`"zh"` 为中文（默认），`"en"` 为英文。AI 按该语言撰写整理稿、建议和新报告标题，生成器切换原稿的说明与标签；聊天原文、引用、姓名和群名保留原文。修改配置不自动翻译旧报告，也不重命名已有文件。通用规则以英文维护，不影响报告默认中文。

以下命令在仓库根目录执行，使用 Python 标准库和已授权的飞书 CLI：

```bash
python3 scripts/sync.py status
python3 scripts/sync.py collect --chat '配置中的名称'
python3 scripts/sync.py export --chat '配置中的名称'
python3 scripts/build_document.py 'output/work/YYYYMMDD/任务目录/topic-index.json'
```

名称定位使用 sync.py resolve，备份核对使用 reconcile_backup.py --source '群名' --backup '姓名' --day YYYY-MM-DD。未启用定时运行；脚本负责采集与保存，AI 负责理解和整理。

## 规则入口

[总边界](AGENTS.md) · [本地技能](.agents/skills/lark-context-ledger/SKILL.md) · [采集规则](rules/sync.md) · [记录规则](rules/records.md) · [沟通回顾](rules/communication.md) · [日志](LOG.md)
