# SendMessage 协作设计

## 1. SendMessage 概述

### 1.1 SendMessage 的作用

SendMessage 是 Claude Code Team 模式中 Agent 之间协作的核心通信机制。通过 SendMessage，多个 Agent 可以在一个团队内协调工作、共享信息、管理状态。

**核心价值：**
- 解耦 Agent 间依赖
- 实现异步协作模式
- 支持灵活的消息传递策略

### 1.2 5 种消息类型及用途

| 消息类型 | 用途 | 典型场景 |
|---------|------|---------|
| `message` | 向特定 Agent 发送直接消息 | 指令派发、数据请求、状态查询 |
| `broadcast` | 向所有团队成员广播消息 | 关键通知、全局事件 |
| `shutdown_request` | 请求某个 Agent 优雅退出 | 团队解散、任务完成 |
| `shutdown_response` | 响应退出请求（同意/拒绝） | 退出确认、延期请求 |
| `plan_approval_response` | 响应计划审批请求 | 计划通过、拒绝并反馈 |

---

## 2. 消息类型详解

### 2.1 type: message - 直接消息

发送给指定收件人的直接消息，是最常用的通信方式。

**JSON 格式：**
```json
{
  "type": "message",
  "recipient": "task-manager",
  "content": "具体指令内容",
  "summary": "简短摘要（5-10词）"
}
```

**参数说明：**
- `type` (必填): 固定值 `"message"`
- `recipient` (必填): 接收消息的 Agent 名称
- `content` (必填): 消息正文，详细说明指令或请求
- `summary` (必填): 消息摘要，5-10 词，用于 UI 预览

**使用场景：**
- 派发具体任务
- 请求数据查询
- 状态同步请求
- 问题反馈

**示例：**
```json
{
  "type": "message",
  "recipient": "task-manager",
  "content": "请创建一个新的任务：完成财务报表生成，截止日期是 2026-02-25",
  "summary": "创建新任务：财务报表生成"
}
```

---

### 2.2 type: broadcast - 广播

向团队中所有 Agent 发送相同消息。

**JSON 格式：**
```json
{
  "type": "broadcast",
  "content": "给所有团队成员的消息",
  "summary": "广播摘要"
}
```

**参数说明：**
- `type` (必填): 固定值 `"broadcast"`
- `content` (必填): 消息正文
- `summary` (必填): 消息摘要，5-10 词

**⚠️ 重要提示：广播谨慎使用**
- 每次广播会向所有团队成员发送独立消息
- N 个团队成员 = N 次消息传递
- 仅在真正需要所有 Agent 关注时使用

**使用场景：**
- 关键系统事件（如：项目启动/完成）
- 阻塞性问题通知
- 团队级别配置变更
- 紧急安全警报

**示例：**
```json
{
  "type": "broadcast",
  "content": "项目 PROJ-001 已正式启动，请各角色准备就绪",
  "summary": "项目 PROJ-001 启动通知"
}
```

---

### 2.3 type: shutdown_request - 请求退出

请求某个 Agent 优雅关闭。

**JSON 格式：**
```json
{
  "type": "shutdown_request",
  "recipient": "task-manager",
  "content": "任务完成，可以退出了"
}
```

**参数说明：**
- `type` (必填): 固定值 `"shutdown_request"`
- `recipient` (必填): 待退出 Agent 的名称
- `content` (可选): 退出原因或说明

**使用场景：**
- 任务全部完成
- 团队解散
- 错误导致需要重启
- 主动终止任务

**示例：**
```json
{
  "type": "shutdown_request",
  "recipient": "task-manager",
  "content": "所有任务已完成，准备解散团队"
}
```

---

### 2.4 type: shutdown_response - 退出响应

响应退出请求，同意或拒绝退出。

**JSON 格式：**
```json
{
  "type": "shutdown_response",
  "request_id": "abc-123",
  "approve": true
}
```

**参数说明：**
- `type` (必填): 固定值 `"shutdown_response"`
- `request_id` (必填): 对应的 shutdown_request 的 request_id
- `approve` (必填): `true` 表示同意退出，`false` 表示拒绝
- `content` (可选): 拒绝时的原因说明

**使用场景：**
- 同意退出并终止
- 拒绝退出并提供原因

**同意退出示例：**
```json
{
  "type": "shutdown_response",
  "request_id": "req-001",
  "approve": true
}
```

**拒绝退出示例：**
```json
{
  "type": "shutdown_response",
  "request_id": "req-001",
  "approve": false,
  "content": "还有 3 个任务正在进行，无法立即退出"
}
```

---

### 2.5 type: plan_approval_response - 计划审批响应

响应来自具有 `plan_mode_required` 的 Agent 的计划审批请求。

**JSON 格式：**
```json
{
  "type": "plan_approval_response",
  "request_id": "abc-123",
  "recipient": "task-manager",
  "approve": true
}
```

**参数说明：**
- `type` (必填): 固定值 `"plan_approval_response"`
- `request_id` (必填): 对应的 plan_approval_request 的 request_id
- `recipient` (必填): 发起计划的 Agent 名称
- `approve` (必填): `true` 表示批准计划，`false` 表示拒绝
- `content` (可选): 拒绝时的反馈意见

**使用场景：**
- 计划审批通过
- 计划被拒绝并要求修改

**批准计划示例：**
```json
{
  "type": "plan_approval_response",
  "request_id": "plan-001",
  "recipient": "task-manager",
  "approve": true
}
```

**拒绝计划示例：**
```json
{
  "type": "plan_approval_response",
  "request_id": "plan-001",
  "recipient": "task-manager",
  "approve": false,
  "content": "请添加错误处理逻辑，再重新提交计划"
}
```

---

## 3. 协作模式

### 3.1 模式 1：请求-响应

一个 Agent 向另一个 Agent 发送请求，接收方处理后响应。

**流程：**
```
Agent A                  Agent B
  |                        |
  |--- message(request) -->|
  |                        | 处理请求
  |<-- message(response) --|
  |                        |
```

**适用场景：**
- 依赖任务需要前置 Agent 完成某些工作
- 数据查询请求
- 状态同步请求
- 信息确认

**特点：**
- 点对点通信
- 同步感强（虽然底层是异步）
- 明确的请求-响应配对

**示例：任务依赖**
```json
// Step 1: schedule-manager 向 task-manager 查询任务状态
{
  "type": "message",
  "recipient": "task-manager",
  "content": "请查询 TASK-2026-02-24-001 的当前状态",
  "summary": "查询任务状态"
}

// Step 2: task-manager 响应查询结果
{
  "type": "message",
  "recipient": "schedule-manager",
  "content": "TASK-2026-02-24-001 状态：进行中，完成度 60%",
  "summary": "返回任务状态"
}
```

---

### 3.2 模式 2：事件驱动

一个 Agent 完成工作后广播完成事件，其他 Agent 监听并触发后续操作。

**流程：**
```
Agent A                  Agent B                  Agent C
  |                        |                        |
  |--- broadcast(event) --->|--- broadcast(event) --->|--- broadcast(event) --->
  |                        |                        |
  |                        | 处理事件               | 处理事件
  |                        | 触发后续操作           | 触发后续操作
```

**适用场景：**
- 流水线操作
- 级联处理
- 多 Agent 协同完成一个复杂任务
- 状态变更通知

**特点：**
- 一对多通信
- 解耦度高
- 适合复杂的协同工作流

**示例：任务完成后的级联处理**
```json
// task-manager 广播任务完成事件
{
  "type": "broadcast",
  "content": "任务 TASK-2026-02-24-001 已完成",
  "summary": "任务 TASK-001 完成"
}

// knowledge-manager 监听并更新知识库
{
  "type": "message",
  "recipient": "knowledge-manager",
  "content": "已收到任务完成通知，更新知识库",
  "summary": "更新知识库"
}

// file-manager 监听并生成报告
{
  "type": "message",
  "recipient": "file-manager",
  "content": "已收到任务完成通知，生成完成报告",
  "summary": "生成完成报告"
}
```

---

### 3.3 模式 3：状态同步

Agent 定期或按需广播状态，团队保持信息同步。

**流程：**
```
Agent A                  团队成员
  |
  |--- broadcast(state) -------------------------------->|
  |                                                    监听状态
  |                                                   更新视图
```

**适用场景：**
- 长时间运行的任务
- 需要全局进度跟踪
- 多 Agent 共享状态信息
- 团队状态监控

**特点：**
- 一对多通信
- 适用于长时间协作
- 保持团队信息一致性

**示例：长时间任务进度同步**
```json
// task-manager 定期广播任务进度
{
  "type": "broadcast",
  "content": "当前任务队列状态：5 个进行中，3 个已完成，2 个待分配",
  "summary": "任务队列状态更新"
}
```

---

## 4. 消息最佳实践

### 4.1 摘要编写规范

**要求：**
- 长度：5-10 词
- 内容：准确概括消息核心
- 语言：简洁明了

**好的摘要示例：**
- ✅ "创建新任务：财务报表生成"
- ✅ "查询任务 TASK-001 状态"
- ✅ "批准任务变更计划"
- ✅ "项目 PROJ-001 启动通知"

**不好的摘要示例：**
- ❌ "你好"（过于简单，未包含实质内容）
- ❌ "我有个问题想问你关于任务的事情"（太长）
- ❌ "Message about task status"（非中文）

---

### 4.2 消息响应规范

**基本原则：**
- 收到消息后及时响应
- 响应内容清晰明确
- 无法立即处理时说明原因和预计时间

**响应示例：**
```json
// 立即响应
{
  "type": "message",
  "recipient": "ceo",
  "content": "已收到指令，正在处理中",
  "summary": "确认收到指令"
}

// 延迟处理
{
  "type": "message",
  "recipient": "ceo",
  "content": "当前有 2 个任务在进行中，预计 10 分钟后开始处理新指令",
  "summary": "延迟处理通知"
}
```

---

### 4.3 广播使用规范

**慎用原则：**
- 只在真正需要所有 Agent 关注时使用
- 避免频繁广播
- 广播内容应当重要且紧急

**适用场景：**
- 系统级事件（项目启动/完成、系统初始化等）
- 阻塞性问题（需要所有 Agent 协同处理）
- 团队级配置变更

**不适用场景：**
- 单个 Agent 之间的普通通信 → 使用 `message`
- 通知特定状态变更 → 使用 `message`

---

### 4.4 拒绝请求规范

**拒绝请求时必须提供：**
1. 明确的拒绝声明
2. 拒绝原因
3. 建议（如有）

**拒绝示例：**
```json
{
  "type": "shutdown_response",
  "request_id": "req-001",
  "approve": false,
  "content": "无法立即退出，因为还有 3 个任务正在进行中。建议等待任务完成后再退出。"
}
```

```json
{
  "type": "plan_approval_response",
  "request_id": "plan-001",
  "recipient": "task-manager",
  "approve": false,
  "content": "计划缺少错误处理逻辑。建议在数据处理部分添加 try-catch 块，并添加日志记录。"
}
```

---

### 4.5 消息历史记录

**建议记录：**
- 所有发送和接收的消息
- 消息时间戳
- 消息处理结果

**记录格式示例：**
```
[2026-02-24 10:30:15] OUTGOING -> task-manager: "创建新任务：财务报表生成"
[2026-02-24 10:30:20] INCOMING <- task-manager: "任务已创建，ID: TASK-001"
```

---

## 5. 常见场景示例

### 5.1 场景 1：数据请求

**场景描述：** knowledge-manager 需要查询今日任务列表

**消息流程：**
```
knowledge-manager → task-manager: "查询今日任务"
task-manager → knowledge-manager: "返回任务列表"
```

**消息示例：**
```json
// Step 1: knowledge-manager 请求数据
{
  "type": "message",
  "recipient": "task-manager",
  "content": "请查询 2026-02-24 的所有任务列表",
  "summary": "查询今日任务列表"
}

// Step 2: task-manager 返回数据
{
  "type": "message",
  "recipient": "knowledge-manager",
  "content": "2026-02-24 任务列表：\n1. TASK-001: 财务报表生成（进行中）\n2. TASK-002: 系统备份（已完成）",
  "summary": "返回今日任务列表"
}
```

---

### 5.2 场景 2：完成通知

**场景描述：** task-manager 完成任务后，其他 Agent 需要更新各自的状态

**消息流程：**
```
task-manager → broadcast: "任务 TASK-001 已完成"
knowledge-manager: 监听并更新知识库
file-manager: 监听并生成报告
```

**消息示例：**
```json
// task-manager 广播完成事件
{
  "type": "broadcast",
  "content": "任务 TASK-2026-02-24-001 已完成，开始时间：2026-02-24 09:00，完成时间：2026-02-24 11:30",
  "summary": "任务 TASK-001 完成"
}

// knowledge-manager 响应（内部逻辑，非直接发送）
// 监听到广播后，自动更新知识库

// file-manager 响应（内部逻辑，非直接发送）
// 监听到广播后，自动生成任务完成报告
```

---

### 5.3 场景 3：团队关闭

**场景描述：** CEO 决定解散团队，依次请求所有成员退出

**消息流程：**
```
CEO → task-manager: shutdown_request
task-manager: shutdown_response(accept)
CEO → file-manager: shutdown_request
file-manager: shutdown_response(accept)
CEO → knowledge-manager: shutdown_request
knowledge-manager: shutdown_response(accept)
...
```

**消息示例：**
```json
// CEO 请求 task-manager 退出
{
  "type": "shutdown_request",
  "recipient": "task-manager",
  "content": "所有任务已完成，准备解散团队"
}

// task-manager 同意退出
{
  "type": "shutdown_response",
  "request_id": "req-001",
  "approve": true
}

// CEO 请求 file-manager 退出
{
  "type": "shutdown_request",
  "recipient": "file-manager",
  "content": "团队准备解散，请完成清理工作后退出"
}

// file-manager 同意退出
{
  "type": "shutdown_response",
  "request_id": "req-002",
  "approve": true
}

// CEO 请求 knowledge-manager 退出
{
  "type": "shutdown_request",
  "recipient": "knowledge-manager",
  "content": "团队准备解散，请保存知识库后退出"
}

// knowledge-manager 同意退出
{
  "type": "shutdown_response",
  "request_id": "req-003",
  "approve": true
}
```

---

### 5.4 场景 4：计划审批

**场景描述：** task-manager（具有 plan_mode_required）提交计划，CEO 审批

**消息流程：**
```
task-manager → CEO: plan_approval_request (plan_mode 自动生成)
CEO → task-manager: plan_approval_response(approve: true)
task-manager: 退出计划模式，开始执行
```

**消息示例：**
```json
// task-manager 退出计划模式后，系统自动生成审批请求
// CEO 审批通过
{
  "type": "plan_approval_response",
  "request_id": "plan-001",
  "recipient": "task-manager",
  "approve": true
}

// task-manager 收到审批后，退出计划模式，开始执行计划
```

---

## 6. 注意事项

### 6.1 消息传递机制

- **自动投递：** 消息通过系统自动投递，无需手动检查收件箱
- **消息去重：** 系统自动处理消息去重
- **失败处理：** 确保消息发送失败时有重试机制

### 6.2 性能考虑

- **广播开销：** N 个团队成员 = N 次消息传递
- **批量操作：** 多个独立操作考虑并行发送
- **消息大小：** content 字段不宜过大，必要时使用外部存储

### 6.3 安全考虑

- **消息验证：** 验证消息来源和完整性
- **敏感信息：** 避免在消息中传递敏感信息
- **权限控制：** 确保消息发送方有权限与接收方通信

---

## 7. 附录

### 7.1 消息类型快速参考

| 消息类型 | recipient | request_id | approve | 适用场景 |
|---------|-----------|------------|---------|---------|
| `message` | ✅ 必填 | ❌ | ❌ | 直接通信 |
| `broadcast` | ❌ | ❌ | ❌ | 全员通知 |
| `shutdown_request` | ✅ 必填 | ❌ | ❌ | 请求退出 |
| `shutdown_response` | ❌ | ✅ 必填 | ✅ 必填 | 响应退出 |
| `plan_approval_response` | ✅ 必填 | ✅ 必填 | ✅ 必填 | 审批计划 |

### 7.2 错误码参考

| 错误码 | 含义 | 处理建议 |
|-------|------|---------|
| `INVALID_TYPE` | 消息类型无效 | 检查 type 字段值 |
| `MISSING_RECIPIENT` | 缺少收件人 | 添加 recipient 字段 |
| `INVALID_REQUEST_ID` | 请求 ID 无效 | 检查 request_id 格式 |
| `APPROVE_MISSING` | 缺少 approve 字段 | 添加 approve 字段 |
| `AGENT_NOT_FOUND` | 目标 Agent 不存在 | 检查 recipient 名称 |

---

**文档版本：** v1.0
**最后更新：** 2026-02-24
**维护者：** OPC-CEO 团队
