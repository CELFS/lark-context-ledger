# lark-context-ledger

[English](README.md) | 简体中文

基于 Lark CLI 采集工作沟通，整理任务与背景，回顾沟通方式，提前发现口径缺口。飞书严格只读，AI 不发送消息、不修改业务数据。

## 使用 Codex 快速开始

### 1. 准备本地环境

- Python 3.9 或更高版本。脚本使用标准库；采集器使用 Unix 文件锁，需要 macOS 或 Linux 环境。
- [Lark CLI／飞书 CLI](https://github.com/larksuite/cli) 及其 Agent Skills。按官方说明完成安装、应用配置和登录，确保 Codex 使用的终端能找到 `lark-cli`，并以用户身份获得目标来源所需的只读权限。采集流程使用官方 `lark-shared`、`lark-im` 技能，其他业务域按相关材料需要准备。
- 能访问本地文件和终端的 Codex。安装与使用入口见 [OpenAI 官方桌面应用说明](https://developers.openai.com/codex/app/)。

CLI 安装和授权由你完成，或在明确授权后交给 AI 操作；提出采集需求不等于授权安装、登录或修改应用配置。

### 2. 在 Codex 中打开本项目

将本地 `lark-context-ledger` 文件夹打开或添加为项目，以这个仓库根目录作为对话工作目录。即使 `output/reports/` 已有独立 Git 仓库，也从工具仓库进入使用流程。

项目已包含 [.agents/skills/lark-context-ledger/SKILL.md](.agents/skills/lark-context-ledger/SKILL.md)。Codex 会发现仓库内 `.agents/skills` 中的技能，无需额外全局安装本项目 skill。保持其在仓库中的位置，以便相对路径能找到规则、模板和脚本。机制见 [OpenAI 本地 skill 文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。如果未显示该技能，先检查项目目录，再重启 Codex。

### 3. 创建本地配置

以 [sources.example.json](config/sources.example.json) 为格式参考，创建 `config/sources.local.json`，填写自己的起始日期 `since`、来源名称 `chats`，并选择报告语言 `report_language`（默认 `zh`，也可选 `en`）。采集前替换示例日期和名称；示例文件不会作为运行配置读取。字段说明见[配置文档](config/sources.md)。

真实配置和整个 `output/` 均由本项目仓库忽略。凭据由飞书 CLI 自身的认证存储管理，不写入该 JSON。

### 4. 先本地检查，再提出采集需求

在仓库根目录检查配置及已保存的采集状态：

```bash
python3 scripts/sync.py status
```

该命令不调用飞书 API，也不验证登录状态或接口权限。首次定位来源前，显示尚未解析是正常情况；登录检查另按 CLI 官方认证说明操作。

第一次向 Codex 提问，可以直接使用：

> 使用 lark-context-ledger。读取 AGENTS.md 和项目 skill，检查我的本地配置，说明已配置的来源与日期范围，暂不查询飞书或采集消息。

确认范围后，再要求 Codex 采集和整理指定来源。结果保存在 `output/reports/`；上述接入步骤不会启用定时任务或持续监听。

## 日常使用

在本地配置填写起始日期与聊天名称，然后在对话中提出需求，例如“整理指定群最近的讨论”“更新任务进展”“回顾这段沟通”。

需要保留个人思考时，明确要求保存为 `thinking`，用于回看讨论和自我提醒原则。普通聊天不会自动保存个人立场，也不代表授权采集飞书。

会话任务提供两份文档；thinking 使用一份带日期的 Markdown 笔记：

以下示例使用中文报告命名（`report_language: "zh"`，默认值）。英文命名示例见 [English README](README.md)。

```text
output/
  reports/YYYYMMDD/
    NN-topic-MMDD_HHmm-MMDD_HHmm-主题-来源/
      YYYYMMDD-主题-整理稿.md      日常阅读
      YYYYMMDD-主题-原文归档.md    原文证据
      attachments/               本地附件，Git 忽略
    NN-watch-MMDD_HHmm-主题-来源/  持续监听，文档结构同上
    NN-thinking-主题/             个人思考
      YYYYMMDD-主题.md            提醒原则、讨论和来源
  work/                          过程材料，Git 忽略
  state/                         同步状态，Git 忽略
```

整理稿用于日常阅读，包含背景、结论、变化和待办；原文归档用于查证，保留说话人、时间、正文和回复关联。`watch` 目录使用相同的两份文档结构；thinking 笔记保留个人思考、提醒原则、讨论整理和来源链接。`attachments/` 保存原附件，仅在本地保留，由报告仓库忽略；`work/` 保存过程材料，`state/` 保存同步状态，两者均由项目仓库忽略。

目录按创建日期归档，NN 为三种类型共用的当天创建顺序，依次追加且不重排。`topic` 表示主题整理，包含消息起止时间；`watch` 表示持续监听，仅含消息起始时间；`thinking` 表示个人思考，不要求消息时间范围或聊天来源。会话后续更新沿用原目录，最新覆盖时间写在正文中；同一篇 thinking 的后续更新也沿用原目录。目录时间统一使用北京时间。命名为 watch 不代表已经启用监听。过程材料按相同日期和任务目录放入 `output/work/`。

会话任务的文件名使用整理日期（YYYYMMDD）、来源或具体主题、文档类型，避免只用“整理稿”或“原文归档”。新文档标签使用配置中的报告语言，README 的语言不改变报告默认语言；实际来源名称保留原文，已有文件名保持不变。正文保留覆盖的消息时间范围。原文每条只保存一次，附件不重复嵌入全文。后续默认先读整理稿，再按需追溯原文；已有资料复用，增量更新。

thinking 通过链接关联相关 topic 和已有证据，不重复复制原文。笔记中的原则属于个人思考，不自动变成项目规则、长期偏好或任务。直接保存 Markdown 笔记即可，不要求运行会话采集脚本或两份文档生成器。

README 仅说明用途与用法；具体需求和结果全部在 output/。根目录 `CHANGELOG.md` 记录 skill、规则、脚本、模板和说明文档等工具变更；实际采集、整理、报告生成与维护操作写入 `output/reports/LOG.md`，按需关联报告。具体任务进展保留在对应报告中。可复用日志格式集中维护在[记录规则](rules/records.md)。

项目仓库忽略整个 `output/`。`output/reports/` 用于独立的本地 Git 仓库，保存报告版本；附件由其内部 `.gitignore` 忽略，过程材料和同步状态不纳入报告仓库。独立仓库由用户手动初始化和提交，不配置远程地址。

## 配置与命令

真实配置使用 `config/sources.local.json`，已 Git 忽略；格式见 [配置说明](config/sources.md) 和 [示例](config/sources.example.json)。必填 since 与 chats；可选 report_language，默认 zh，支持 zh/en。名称定位由工具处理，重名先确认。

报告语言由本地 JSON 的 `report_language` 控制：`"zh"` 为中文（默认），`"en"` 为英文。AI 按该语言撰写整理稿、建议和新报告标题，生成器切换原稿的说明与标签；聊天原文、引用、姓名和群名保留原文。修改配置不自动翻译旧报告，也不重命名已有文件。通用规则以英文维护，不影响报告默认中文。`CHANGELOG.md` 和 `output/reports/LOG.md` 始终使用英文，不受 `report_language` 影响。

以下命令在仓库根目录执行，使用 Python 标准库和已授权的飞书 CLI：

```bash
python3 scripts/sync.py status
python3 scripts/sync.py collect --chat '配置中的名称'
python3 scripts/sync.py export --chat '配置中的名称'
python3 scripts/build_document.py 'output/work/YYYYMMDD/任务目录/topic-index.json'
```

名称定位使用 sync.py resolve，备份核对使用 reconcile_backup.py --source '群名' --backup '姓名' --day YYYY-MM-DD。未启用定时运行；脚本负责采集与保存，AI 负责理解和整理。

## 规则入口

[总边界](AGENTS.md) · [本地技能](.agents/skills/lark-context-ledger/SKILL.md) · [采集规则](rules/sync.md) · [记录规则](rules/records.md) · [沟通回顾](rules/communication.md) · [工具变更记录](CHANGELOG.md)
