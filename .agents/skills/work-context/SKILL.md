---
name: work-context
description: 在 work-context 仓库内采集已授权的飞书信息，整理事项背景和本地任务状态，回顾沟通并给出建议。用于信息同步、口径梳理、任务进展和个人沟通复盘；禁止发送消息或修改任何飞书业务数据。
---

# 工作上下文维护

以仓库根目录的 [AGENTS.md](../../../AGENTS.md) 为边界。所有“同步状态”均指更新本地，所有建议仅给用户，不执行飞书业务操作。

## 按需读取

- 采集或监听：读取 [config/sources.md](../../../config/sources.md)、本地 `config/sources.local.json` 和 [rules/sync.md](../../../rules/sync.md)。实际使用飞书 CLI 前，读取已安装的 `lark-shared` 及对应领域技能；这些技能中的发送或写入能力不构成本项目授权。
- 整理通知、背景、任务：读取 [rules/records.md](../../../rules/records.md)，按 [templates/topic.md](../../../templates/topic.md) 记录。
- 分析口径、效率、表达、态度或个人沟通：读取 [rules/communication.md](../../../rules/communication.md)，按 [templates/review.md](../../../templates/review.md) 回顾。

- 用户要求按话题保留完整原文并独立整理章节：读取 [rules/records.md](../../../rules/records.md) 的“完整原文归档”；将本次需求和执行范围记录在 output/records/tasks/<任务ID>/archive.md，再采集、归类与生成文档。skill 只保留通用执行方式，不写具体任务内容。

## 执行顺序

1. 确认本轮是采集、整理还是回顾。优先读取本轮新增资料、用户反馈和相关事项的最新状态，不全量重读历史。
2. 核对来源、时间、消息标识及上下文；缺失的证据明确标注，不补造。采集配置未确认时不调用飞书。
3. 将同一事项的新证据合并到已有记录；任务、通知、探索分别识别，建议不自动成为正式任务。
4. 将业务记录写入 `output/records/`，运行数据写入 `output/state/`，报告写入 `output/reports/`。更新事项当前状态并在 output/ 内追加任务 LOG；根 LOG 仅记录不含具体业务内容的维护或运行日志，不写具体任务入口或结论。
5. 检查来源可追溯、关闭状态未被旧消息重开、未新增无依据的期限或责任人，以及没有执行远端写入。
6. 用户主动询问时直接回答。后台运行只在有意义的进展、待办变化、明确行动需要或采集异常时提醒；无变化保持静默。尚未建立后台运行能力时，不承诺持续监听。

当来源不可读、权限不足或记录不完整时，保留本地旧状态，说明具体缺口；不扩大读取范围，不改用其他身份，不伪报成功。
