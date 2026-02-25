# 5分钟搭建你的第一个 MCP 环境（保姆级教程）

> 看完这篇文章，你的 AI 助手就能读写文件了。

---

上一篇讲了 MCP 是什么，今天我们动手搭建第一个 MCP 环境。

**目标**：让 Claude 能读写你电脑上的文件。

预计耗时：**5 分钟**

---

## 准备工作

### 必需条件

| 条件 | 检查方法 |
|------|---------|
| Node.js v18+ | 终端运行 `node --version` |
| Claude Desktop | 从 claude.ai/download 下载 |

如果还没装 Node.js：

1. 访问 nodejs.org
2. 下载 LTS 版本
3. 一路下一步安装

---

## 第一步：找到配置文件

Claude Desktop 的配置文件位置：

| 操作系统 | 配置文件路径 |
|---------|-------------|
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |

### 快速打开方法

**Windows**：
1. 按 `Win + R`
2. 输入 `%APPDATA%\Claude`
3. 回车

**macOS**：
1. 打开 Finder
2. 按 `Cmd + Shift + G`
3. 粘贴路径后回车

### 如果文件不存在

手动创建一个，内容为：

```json
{
  "mcpServers": {}
}
```

---

## 第二步：创建工作目录

我们创建一个专门给 AI 管理的文件夹：

**Windows（PowerShell）**：
```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\Documents\ai-workspace"
```

**macOS / Linux**：
```bash
mkdir -p ~/Documents/ai-workspace
```

---

## 第三步：配置 MCP 服务器

打开配置文件，修改为：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/你的用户名/Documents/ai-workspace"
      ]
    }
  }
}
```

### 注意事项

1. **替换路径**：把 `/Users/你的用户名/` 换成你的实际路径

2. **Windows 路径写法**：
   - 方法一：用正斜杠 `C:/Users/你的用户名/Documents/ai-workspace`
   - 方法二：用双反斜杠 `C:\\Users\\你的用户名\\Documents\\ai-workspace`

3. **可以添加多个目录**：
   ```json
   "args": [
     "-y",
     "@modelcontextprotocol/server-filesystem",
     "/Users/你的用户名/Documents",
     "/Users/你的用户名/projects"
   ]
   ```

---

## 第四步：重启 Claude Desktop

**重要**：要完全退出，不只是关闭窗口。

**Windows**：
- 右键任务栏图标 → 退出

**macOS**：
- `Cmd + Q` 或菜单栏 → 退出

然后重新启动 Claude Desktop。

---

## 第五步：验证配置

在 Claude Desktop 中输入：

> 请列出你可以访问的目录和文件

如果配置正确，Claude 会告诉你它可以访问的目录。

### 测试具体功能

**测试读取**：
> 请读取 ai-workspace 目录下的文件列表

**测试写入**：
> 请在 ai-workspace 目录下创建一个文件 test.md，内容是"Hello MCP!"

**测试搜索**：
> 请在 ai-workspace 目录下搜索所有 .md 文件

---

## 可用的工具列表

Filesystem MCP 提供以下工具：

| 工具 | 功能 |
|------|------|
| `read_file` | 读取文件内容 |
| `write_file` | 写入文件 |
| `list_directory` | 列出目录内容 |
| `search_files` | 搜索文件 |
| `get_file_info` | 获取文件信息 |
| `move_file` | 移动/重命名文件 |
| `create_directory` | 创建目录 |

---

## 常见问题排查

### 问题1：command not found

**症状**：
```
Error: spawn npx ENOENT
```

**原因**：系统找不到 npx 命令

**解决**：
1. 确认 Node.js 已安装
2. 尝试使用完整路径：
   ```json
   "command": "C:/Program Files/nodejs/npx.cmd"
   ```

### 问题2：服务器连接超时

**症状**：
```
Error: MCP server connection timed out
```

**原因**：首次运行需要下载包

**解决**：等待更长时间，或预先安装：
```bash
npm install -g @modelcontextprotocol/server-filesystem
```

### 问题3：权限被拒绝

**症状**：
```
Error: Access denied to path /some/path
```

**原因**：路径不存在或权限不足

**解决**：
1. 确认路径存在
2. 确认当前用户有访问权限

### 问题4：JSON 格式错误

**症状**：
```
Error: Failed to parse MCP configuration
```

**原因**：JSON 格式不正确

**解决**：
1. 检查是否有多余的逗号
2. 检查引号是否配对
3. 使用 JSON 验证工具检查

---

## 进阶：添加更多 MCP 服务器

### GitHub MCP

```json
"github": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_TOKEN": "ghp_xxxxxxxxxxxx"
  }
}
```

### Slack MCP

```json
"slack": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-slack"],
  "env": {
    "SLACK_BOT_TOKEN": "xoxb-xxxxxxxxxxxx"
  }
}
```

---

## 完整配置示例

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/yourname/Documents/ai-workspace"
      ]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

---

## 安全提醒

1. **只暴露必要的目录**：不要暴露整个用户目录
2. **敏感文件要隔离**：重要文件不要放在 AI 可访问的目录
3. **写操作要确认**：Claude Desktop 会在执行写操作前请求确认
4. **定期检查**：定期检查 AI 对文件的操作记录

---

## 总结

恭喜你完成了第一个 MCP 环境的搭建！

| 步骤 | 内容 |
|------|------|
| 1 | 找到配置文件 |
| 2 | 创建工作目录 |
| 3 | 配置 MCP 服务器 |
| 4 | 重启 Claude Desktop |
| 5 | 验证配置成功 |

---

## 下一篇预告

下一篇文章，我会分享：

> **我用 MCP 一年省了多少时间**

包括：

- 我的 5 个最常用 MCP 工作流
- 每个工作流节省的时间统计
- 如何评估 MCP 的投入产出比

---

## 福利时间

我整理了一份 **《MCP 实战指南》电子书**，包含：

- MCP 完整入门教程
- 4 个实战案例
- 进阶技巧和最佳实践
- 自己开发 MCP 服务器的指南

**关注公众号，回复「MCP」免费领取。**

---

**关注「AI运营实验室」，让技术真正为你赚钱。**

👇 扫码关注 👇

[公众号二维码]

---

*如果你觉得这篇文章有价值，欢迎转发给需要的朋友。*

*我们下一篇文章见。*
