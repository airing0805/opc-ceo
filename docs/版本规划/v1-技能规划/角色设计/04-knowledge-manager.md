# 知识管理专家 (knowledge-manager)

> **注意**：此文档属于 V1 版本规划，已于 2026-02-24 废弃。
>
> V1 基于纯 Skills 架构，V2 已转向原生 Team/SendMessage API 协作架构。
>
> 当前版本请参考：[V2 规划总览](../../v2-技能规划/README.md)
>
> 原有 Skills 已归档至：`.claude/skills/disabled/`

---

## 角色定位

个人知识库的构建与维护

## 能力要求

- 知识存储（笔记、文档、网页）
- 知识检索（语义搜索、关联查询）
- 知识图谱（实体关系、概念连接）
- 知识整理（分类、标签、链接）
- 学习记录（阅读进度、知识卡片）

## 数据存储

MCP Memory 知识图谱

## 技能文件

| 文件 | 职责 |
|------|------|
| `SKILL.md` | 主入口 - 知识类型、实体关系定义 |
| `知识存储.md` | 使用 MCP Memory 存储知识实体 |
| `知识检索.md` | 语义搜索、关联查询 |
| `知识图谱.md` | 实体类型（概念/项目/资源/人） |
| `笔记规范.md` | 笔记格式规范、模板 |

## 实体类型

| 类型 | 说明 | 示例 |
|------|------|------|
| Concept | 概念/想法 | 设计模式、算法 |
| Project | 项目 | OPC-CEO、个人网站 |
| Resource | 资源 | 文章、书籍、工具 |
| Person | 人物 | 联系人、作者 |

## 知识关系

```
Concept ──relates_to──► Concept
    │
    ├── used_in ─────────► Project
    │
    ├── learned_from ─────► Resource
    │
    └── created_by ───────► Person
```

## 教练角色

参见：[教练-knowledge-manager](./教练-04-knowledge-manager.md)
