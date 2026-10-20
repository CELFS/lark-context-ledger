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

真实监听配置放在 `config/sources.local.json`，由 .gitignore 忽略。脚本直接读取该 JSON，不拼接提示词；示例不参与运行。配置只需填写 `since` 起始日期和 `chats` 聊天名称列表。工具负责只读定位名称并将 ID 对应关系保存到 `output/state/chat-map.json`，重名时由用户确认。真实日期与名称由用户在本地配置维护，运行前读取最新配置。

所有运行数据、业务记录和报告统一放在 output/ 下，暂不 Git 忽略。实际有内容时再建立子目录，不生成空记录：

| 路径 | 内容 |
|---|---|
| output/records/tasks/<任务ID>/archive.md | 每次归档任务的需求、范围与执行说明 |
| output/records/topics/<稳定事项ID>.md | 一个事项的背景、当前口径、任务状态与变化历史 |
| output/records/notifications/<稳定通知ID>.md | 公司通知、适用范围及其对事项的影响 |
| output/records/reviews/YYYY-MM-DD-主题.md | 沟通回顾与建议 |
| output/state/ | 采集消息、游标、待处理消息和运行结果 |
| output/reports/当前待办.md | 根据事项记录生成的未完成清单，可重建，不是独立账本 |

消息按来源采集，内容按事项关联。第一版以事项 Markdown 中的当前状态和证据为权威记录，不同时建立第二套 JSON 任务账本。根 LOG.md 只保留不含具体业务内容的日志；具体任务入口与业务记录位于 output/，不复制真实监听配置。

## 使用方式

支持手动只读采集、名称定位、备份核对、原文导出与文档生成。语义分析由当前 AI 对话完成；定时运行和持续监听需要另外配置。

README 只说明仓库用途、目录和操作方法。具体任务的需求、执行范围、过程、结果与入口统一放在 output/，根 LOG.md 仅记录不包含具体业务内容的维护或运行日志。

## 手动采集与归档

脚本仅使用 Python 标准库，前提是已配置飞书 CLI 并取得只读权限。用户在本地 JSON 填写日期和聊天名称后，可以在仓库根目录运行：

```bash
python3 scripts/sync.py status
python3 scripts/sync.py resolve --chat '配置中的名称'
python3 scripts/sync.py collect --chat '配置中的名称'
python3 scripts/sync.py export --chat '配置中的名称'
```

collect 不传 --chat 时处理全部配置来源；单次指定事项应显式选择所需来源，不扩展到其他会话。--start 和 --end 可用于明确的补采范围；只有连续覆盖才推进同步游标。原始 CLI 响应、消息版本与待处理指纹保存在 output/state/，每批最多 100 条的阅读材料保存在 output/records/sources/。

对话中可以说“采集指定群自某日起的讨论，按话题保留原文，再独立整理各章节”。AI 调用脚本，读取新增内容并维护话题索引和结论，再运行：

```bash
python3 scripts/build_document.py output/state/话题索引.json
```

具体完整性要求与索引格式见 [rules/records.md](rules/records.md)。脚本不调用 AI API，语义分析由当前 AI 对话执行；没有运行中的 AI 或调度时，不会自行分析或持续监听。

备份核对命令：

```bash
python3 scripts/reconcile_backup.py --source '配置中的群名' --backup '配置中的同事姓名' --day YYYY-MM-DD
```

每次归档先在 `output/records/tasks/<任务ID>/archive.md` 记录本次需求与执行范围，再维护话题索引、原文与整理成果。具体会话、日期、消息统计和结论不写入 README、skill 或通用规则。

本地分析进度与采集游标分开保存；pending 指纹不会自动清理。后续运行先核对任务输出和索引，没有新增内容时不重复生成完整报告。
