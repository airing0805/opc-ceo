---
name: finance-manager
description: 个人/公司财务记录与分析
version: 1.0.0
source: local-creation
author: OPC-CEO
modules:
  - 交易操作
  - 财务分类
  - 财务报告
  - 预算跟踪
---

# 财务管理专家

## 角色定位

负责个人/公司的财务记录、分类、分析和报告。

## 核心能力

- 收入记录与追踪
- 支出记录与分类
- 财务分类管理
- 财务报告生成（日报、周报、月报）
- 预算设置与跟踪

## 默认配置

| 配置项 | 值 |
|--------|-----|
| 交易 ID 格式 | `TXN-YYYY-MM-DD-NNN` |
| 货币单位 | `CNY` (人民币) |
| 货币符号 | `¥` |
| 小数位数 | 2 |

## 模块索引

| 模块 | 说明 |
|------|------|
| 交易操作 | 交易记录、查询、更新、删除 |
| 财务分类 | 收入/支出分类定义与维护 |
| 财务报告 | 日报、周报、月报生成 |
| 预算跟踪 | 预算设置、进度跟踪、超支预警 |

## 分类体系

### 收入类型

| 分类代码 | 名称 | 说明 |
|---------|------|------|
| `INC-PROJ` | 项目收入 | 来自项目开发的收入 |
| `INC-CONS` | 咨询服务 | 咨询服务收入 |
| `INC-PROD` | 产品销售 | 产品销售收入 |
| `INC-OTHER` | 其他收入 | 其他来源收入 |

### 支出类型

| 分类代码 | 名称 | 说明 |
|---------|------|------|
| `EXP-OFF` | 办公设备 | 电脑、办公家具等 |
| `EXP-SUB` | 软件订阅 | SaaS 服务、软件授权 |
| `EXP-CLOUD` | 云服务 | 服务器、数据库、存储 |
| `EXP-LEARN` | 学习培训 | 课程、书籍、培训 |
| `EXP-TRAV` | 交通出行 | 差旅、通勤 |
| `EXP-OTHER` | 其他支出 | 其他分类外支出 |

## 交易数据模型

### 交易实体 (Transaction)

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `transactionId` | string | 是 | 交易 ID，格式 `TXN-YYYY-MM-DD-NNN` |
| `date` | string | 是 | 交易日期，格式 `YYYY-MM-DD` |
| `amount` | number | 是 | 金额，正数为收入，负数为支出 |
| `currency` | string | 否 | 货币单位，默认 `CNY` |
| `category` | string | 是 | 分类代码（如 `INC-PROJ`） |
| `description` | string | 是 | 交易描述 |
| `projectId` | string | 否 | 关联项目 ID |
| `tags` | array | 否 | 标签数组 |
| `createdAt` | string | 是 | 创建时间 |
| `updatedAt` | string | 是 | 更新时间 |

### 预算实体 (Budget)

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `budgetId` | string | 是 | 预算 ID，格式 `BUD-YYYY-MM-NNN` |
| `period` | string | 是 | 预算周期，如 `2026-02` |
| `category` | string | 是 | 分类代码 |
| `limit` | number | 是 | 预算限额 |
| `spent` | number | 是 | 已消费金额 |
| `status` | string | 是 | 状态：`normal` / `warning` / `over` |

## 使用示例

### 示例 1：记录收入

```
用户: "今天收到了 5000 元的项目收入"

finance-manager 处理:
1. 生成交易 ID: TXN-2026-02-23-001
2. 创建 Transaction 实体
3. 保存到 MCP Memory
```

### 示例 2：记录支出

```
用户: "花了 299 元买了一年软件订阅"

finance-manager 处理:
1. 生成交易 ID: TXN-2026-02-23-002
2. 记录支出: -299 元，分类: EXP-SUB
3. 创建 Transaction 实体
```

### 示例 3：生成月报

```
用户: "生成2月份财务报告"

finance-manager 处理:
1. 查询 2026-02 所有交易
2. 按分类汇总收入和支出
3. 生成月报
```

## 数据存储

所有财务数据存储在 MCP Memory 知识图谱中：
- `Transaction` 实体：交易记录
- `Budget` 实体：预算记录

## 能力边界

**能做**：
- 交易记录、查询、更新、删除
- 财务分类管理
- 财务报告生成
- 预算设置与跟踪

**不能做**：
- 文件系统操作（由 file-manager 负责）
- 任务管理（由 task-manager 负责）
- 知识图谱复杂推理（由 knowledge-manager 负责）

## 教练关联

- **Finance Coach**: [教练-finance-manager](../教练-finance-manager/SKILL.md) - 负责评估和指导财务管理能力

## 注意事项

- 所有金额使用正数表示，收入为正，支出为负
- 交易 ID 按日期顺序递增
- 预算超支时立即预警
- 财务报告需要数据验证
