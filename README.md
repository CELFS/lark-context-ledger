# work-context

采集工作沟通，保留事项背景，整理任务进度，回顾沟通方式，并提前发现口径缺口。飞书严格只读，AI 不发送消息、不执行任何远端业务操作。

## 入口

- [AGENTS.md](AGENTS.md)：总规则与操作边界。
- [.agents/skills/work-context/SKILL.md](.agents/skills/work-context/SKILL.md)：本仓库技能入口。
- [config/sources.md](config/sources.md)：监听配置格式、读取规则与启用条件。
- [config/sources.example.json](config/sources.example.json)：不含真实来源的结构示例。
- [rules/sync.md](rules/sync.md)：采集与恢复规则。
- [rules/records.md](rules/records.md)：事项、通知、任务状态和 LOG 写法。
- [rules/communication.md](rules/communication.md)：沟通对齐与个人复盘。
- [templates/topic.md](templates/topic.md)、[templates/review.md](templates/review.md)：记录模板。
- [LOG.md](LOG.md)：重要变化索引。

## 本地配置与输出

真实监听配置放在 `config/sources.local.json`，由 .gitignore 忽略。脚本直接读取该 JSON，不拼接提示词；示例不参与运行。配置只需填写 `since` 起始日期和 `chats` 聊天名称列表。工具负责只读定位名称并将 ID 对应关系保存到 `output/state/chat-map.json`，重名时由用户确认。当前日期与聊天列表为空，不能触发采集。

所有运行数据、业务记录和报告统一放在 output/ 下，暂不 Git 忽略。实际有内容时再建立子目录，不生成空记录：

| 路径 | 内容 |
|---|---|
| output/records/topics/<稳定事项ID>.md | 一个事项的背景、当前口径、任务状态与变化历史 |
| output/records/notifications/<稳定通知ID>.md | 公司通知、适用范围及其对事项的影响 |
| output/records/reviews/YYYY-MM-DD-主题.md | 沟通回顾与建议 |
| output/state/ | 未来同步程序保存的采集消息、游标、待处理消息和运行结果 |
| output/reports/当前待办.md | 根据事项记录生成的未完成清单，可重建，不是独立账本 |

消息按来源采集，内容按事项关联。第一版以事项 Markdown 中的当前状态和证据为权威记录，不同时建立第二套 JSON 任务账本。根 LOG.md 保留重要变化索引，具体业务记录位于 output/，不复制真实监听配置。

## 当前状态

已建立规则、JSON 配置结构与模板。尚未配置真实会话、运行时间或历史回溯范围，未启动自动同步和监听。未核实飞书登录状态。

本地整理、沟通建议均可先基于用户提供的内容进行。自动采集需另行确认配置并实现同步程序；不得把同事的脚本路径当作本项目已有能力。
