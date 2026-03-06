# Okeanos AI Platform - Agent 执行指南（中文）

Version: 1.0  
Date: 2026-03-03

## 1. 目的

本文件定义工程 Agent 如何实现 Okeanos AI Platform 的 MVP。  
内容整合自以下文档：
1. `Okeanos_AI_Platform_PRD.md`
2. `docs/architecture.md`
3. `docs/tech_design.md`
4. `docs/execution_plan.md`

## 2. 文档优先级

如发生冲突，按以下优先级执行：
1. `Okeanos_AI_Platform_PRD.md`（业务目标与规则）
2. `docs/tech_design.md`（实现细节）
3. `docs/architecture.md`（系统架构基线）
4. `docs/execution_plan.md`（交付节奏与排期）

## 3. MVP 固定约束

1. 交付周期：6周，`2026-03-03` 到 `2026-04-12`。
2. MVP 包含全部 6 个模块：
   - Campaign
   - Budget
   - Audience
   - SEO
   - Email and SMS
   - Reporting
3. 技术栈：
   - FastAPI
   - PostgreSQL
   - Redis
   - Celery（worker + scheduler）
4. 部署平台：Railway。
5. 集成范围：
   - Meta Ads
   - Google Ads
   - TikTok Ads
   - WordPress REST（含 Contact Form 7 webhook）
   - Gmail API
   - Twilio
6. 交付方式：人工 + 半自动；高风险动作必须审批。
7. MVP 不做后台 UI。

## 4. 系统职责

1. 接收并处理来自 Contact Form 7 的线索。
2. 每小时从三大广告平台拉取数据。
3. 执行预算、消息、合规策略校验。
4. 通过邮件审批编排 Campaign/Budget 高风险动作。
5. 执行邮件与短信序列并严格遵守发送限制。
6. 每周一美东时间 08:00 生成周报。

## 5. 不可违反业务规则

1. CASL 合规：
   - 每封邮件必须带退订链接。
   - 每条短信必须包含 STOP 退订说明。
   - 退订必须在 24 小时内生效。
2. 消息频控：
   - 每个线索每周最多 3 封邮件。
   - 每个线索每 48 小时最多 1 条短信。
   - 短信发送窗口仅限美东时间 09:00-20:00。
3. 预算治理：
   - 未经明确审批不得超出周预算上限。
   - 单平台预算占比超过 60% 需人工覆盖。
4. Campaign 治理：
   - 未有至少一个已审批创意不得启动 Campaign。
   - A/B 测试未满 72 小时不得宣告胜出。
5. 报表要求：
   - 周报必须在每周一 08:00 ET 自动执行。
   - 报表保留 24 个月。

## 6. MVP 数据与 API 基线

1. `docs/tech_design.md` 与 `docs/architecture.md` 定义的 P0 表必须全部落地后才能上线。
2. `docs/tech_design.md` 第 5.1 节定义的 20 个 MVP 端点必须全部实现并通过测试。
3. 新增 API 或变更 schema 时，必须同步更新：
   - `docs/tech_design.md`
   - `docs/execution_plan.md`（若影响排期）

## 7. 运行指标目标（SLO）

1. API p95 延迟 < 400ms（内部操作）。
2. 每小时同步任务 p95 耗时 < 10 分钟。
3. 告警从触发到生成 < 15 分钟。
4. 周报生成时间 < 5 分钟。

## 8. 安全与审计要求

1. 所有 webhook 必须进行 secret/signature 校验。
2. 密钥仅存储于 Railway 环境变量。
3. 受众上传前对 PII 执行 SHA-256 哈希。
4. 消息发送与审批执行必须具备幂等控制。
5. 以下关键动作必须写入不可变审计日志：
   - campaign 变更
   - budget 变更
   - 消息发送
   - 审批决策与执行

## 9. 工程执行流程

每项任务都必须按以下顺序执行：
1. 映射 PRD 对应需求条款。
2. 先实现最小可合规行为。
3. 补齐测试：
   - 规则单元测试
   - connector/webhook 集成测试
   - 关键业务链路 E2E
4. 验证可观测性：
   - 结构化日志
   - 任务/同步状态
   - 错误分类
5. 如行为或契约变更，必须更新文档。

## 10. 周度执行优先级

1. Week 1（2026-03-03 到 2026-03-08）：基础设施与 P0 schema。
2. Week 2（2026-03-09 到 2026-03-15）：Meta/Google/TikTok 数据接入。
3. Week 3（2026-03-16 到 2026-03-22）：campaign/budget/audience + 审批流。
4. Week 4（2026-03-23 到 2026-03-29）：消息引擎 + CASL 执行。
5. Week 5（2026-03-30 到 2026-04-05）：SEO 流程 + 报表 + 告警。
6. Week 6（2026-04-06 到 2026-04-12）：稳定性加固、演练、上线准备。

## 11. 完成定义（Definition of Done）

某功能仅在以下全部满足时视为完成：
1. 覆盖对应 PRD 需求。
2. API/schema 契约已文档化。
3. 正常与异常路径测试通过。
4. 关键动作产生审计日志。
5. 监控与告警信号可用。
6. 不破坏合规规则。

## 12. Agent 升级处理规则

出现以下任一情况需立即升级处理：
1. PRD 与现有实现发生冲突。
2. 关键集成凭据缺失或失效。
3. 稳定性指标持续不达标。
4. 当前设计无法满足合规要求。
5. 时间风险导致 P0 范围无法按期交付。

