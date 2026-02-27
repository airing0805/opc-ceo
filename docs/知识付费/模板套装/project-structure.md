# 项目结构模板

## 推荐目录结构

```
{项目名称}/
├── .claude/                    # Claude Code 配置目录
│   ├── settings.json           # Claude Code 设置
│   ├── commands/               # 自定义命令
│   │   └── {命令名}.md
│   └── skills/                 # 技能目录
│       ├── {skill-name}/       # 技能文件夹
│       │   ├── SKILL.md        # 技能主文件
│       │   ├── {模块名}.md     # 功能模块
│       │   └── 快速参考.md     # 快速参考
│       └── disabled/           # 已禁用技能
│
├── docs/                       # 文档目录
│   ├── 规划体系/               # 规划文档
│   ├── 战略规划/               # 战略目标
│   ├── 沟通文档/               # 沟通记录
│   │   ├── 任务分配.md
│   │   ├── 汇报总结.md
│   │   └── 协调记录.md
│   └── 运营规划/               # 运营计划
│
├── scripts/                    # 脚本目录
│   ├── setup.sh               # 初始化脚本
│   └── sync.sh                # 同步脚本
│
├── tmp/                        # 临时文件目录
│
├── CLAUDE.md                   # 项目配置文件
└── README.md                   # 项目说明文件
```

## 目录说明

| 目录 | 用途 | 必要性 |
|------|------|--------|
| `.claude/` | Claude Code 配置 | 必须 |
| `.claude/skills/` | 技能定义 | 必须 |
| `.claude/settings.json` | Claude Code 设置 | 必须 |
| `docs/` | 项目文档 | 推荐 |
| `docs/规划体系/` | 规划文档 | 推荐 |
| `docs/沟通文档/` | 沟通记录 | 推荐 |
| `scripts/` | 自动化脚本 | 可选 |
| `tmp/` | 临时文件 | 可选 |

## 文件说明

### 必需文件

| 文件 | 说明 |
|------|------|
| CLAUDE.md | 项目级配置文件，让 Claude 理解项目 |
| README.md | 项目说明文件 |

### 配置文件

| 文件 | 说明 |
|------|------|
| `.claude/settings.json` | Claude Code 全局设置 |

## 使用方法

1. 创建项目目录
2. 复制上述目录结构
3. 根据项目需求调整目录和文件
4. 配置 CLAUDE.md 中的项目信息
5. 创建所需的 Skill 和 Agent

## 示例项目

参考项目结构示例：

```
my-company/
├── .claude/
│   ├── settings.json
│   ├── commands/
│   │   └── hello.md
│   └── skills/
│       ├── ceo-core/
│       │   ├── SKILL.md
│       │   └── 快速参考.md
│       └── task-manager/
│           ├── SKILL.md
│           └── 任务操作.md
├── docs/
│   ├── 战略规划/
│   │   └── 愿景.md
│   └── 运营规划/
│       └── 内容计划.md
├── scripts/
│   └── setup.sh
├── tmp/
├── CLAUDE.md
└── README.md
```
