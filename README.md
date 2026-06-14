# 📊 AgentScribe

> **AI编码代理会话记录与智能分析工具**
> Record, analyze and visualize AI coding agent sessions (Claude Code, Cursor, Windsurf, Copilot)

<p align="center">
  <img src="agentscribe_logo.jpg" alt="AgentScribe Logo" width="300" style="border-radius: 16px;">
</p>

<p align="center">
  <a href="https://github.com/gitstq/agentscribe"><img src="https://img.shields.io/github/stars/gitstq/agentscribe?style=flat-square&logo=github" alt="GitHub Stars"></a>
  <a href="https://github.com/gitstq/agentscribe/blob/main/LICENSE"><img src="https://img.shields.io/github/license/gitstq/agentscribe?style=flat-square" alt="MIT License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python" alt="Python 3.10+"></a>
  <a href="https://github.com/gitstq/agentscribe/releases"><img src="https://img.shields.io/github/v/release/gitstq/agentscribe?style=flat-square" alt="Latest Release"></a>
  <a href="https://github.com/gitstq/agentscribe/issues"><img src="https://img.shields.io/github/issues/gitstq/agentscribe?style=flat-square" alt="Issues"></a>
</p>

---

## 🎉 项目介绍

**AgentScribe** 是一款面向 AI 编码代理的**会话记录与智能分析工具**。它可以记录、回放和分析您与 AI 编码代理（如 Claude Code、Cursor、Windsurf、GitHub Copilot、Codex 等）的交互会话，帮助您：

- 📈 **了解代理行为** - 追踪每个会话中的决策过程和工具调用
- 💰 **优化 Token 成本** - 统计 Token 消耗，估算使用成本
- 🔍 **回溯历史会话** - 快速搜索和回放之前的编码会话
- 📊 **生成分析报告** - 输出美观的 HTML 可视化报告
- 🧠 **发现使用模式** - 识别高频工具调用和编码模式

> **设计理念：** 本地优先，数据隐私至上。所有会话数据存储在您的本地 SQLite 数据库中，无需网络连接，无数据泄露风险。

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🎬 **会话录制** | 交互式录制 AI 编码代理的完整会话，包括用户消息、AI 回复和工具调用 |
| 📋 **会话列表** | 按时间、代理、模型等维度快速浏览历史会话 |
| 🔍 **详情查看** | 深入查看每条消息内容、Token 消耗和工具调用详情 |
| 📊 **全局统计** | 汇总所有会话的 Token、成本和时长的统计分析 |
| 📈 **HTML 报告** | 生成美观的交互式 HTML 分析报告，便于分享和归档 |
| 💾 **数据导出** | 支持 JSON 和 Markdown 格式导出会话记录 |
| 🤖 **多代理支持** | 兼容 Claude Code、Cursor、Windsurf、GitHub Copilot、Codex 等主流 AI 编码代理 |
| 🖥️ **交互式仪表盘** | 内置交互式命令行仪表盘，一站式管理所有会话 |
| 🏷️ **标签系统** | 为会话添加自定义标签，便于分类和检索 |
| 🧹 **数据管理** | 支持会话删除和批量清理功能 |

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- pip（Python 包管理器）

### 一键安装

```bash
# 方式一：pip 安装（推荐）
pip install agentscribe

# 方式二：从源码安装
git clone https://github.com/gitstq/agentscribe.git
cd agentscribe
pip install -e .

# 方式三：使用安装脚本
chmod +x scripts/install.sh
./scripts/install.sh
```

### 验证安装

```bash
agentscribe --version
agentscribe --help
```

---

## 📖 详细使用指南

### 📋 列出会话

```bash
# 列出最近 20 条会话
agentscribe list

# 筛选特定代理
agentscribe list --agent claude-code

# JSON 格式输出
agentscribe list --json
```

### 🎬 录制新会话

```bash
# 交互式录制
agentscribe record

# 指定代理和模型
agentscribe record --agent cursor --model gpt-4o --project /path/to/project

# 添加标签
agentscribe record --tag frontend --tag refactor
```

### 🔍 查看会话详情

```bash
# 查看指定会话详情
agentscribe view session_20260614_1a2b3c4d

# JSON 格式输出
agentscribe view session_20260614_1a2b3c4d --json
```

### 📊 查看统

```bash
# 查看全局统计数据
agentscribe stats
```

### 📈 生成报告

```bash
# 生成 HTML 分析报告
agentscribe report

# 指定输出路径并自动打开
agentscribe report --output ./report.html --open
```

### 💾 导出会话

```bash
# 导出为 JSON
agentscribe export session_20260614_1a2b3c4d

# 导出为 Markdown
agentscribe export session_20260614_1a2b3c4d --format markdown
```

### 🗑️ 删除会话

```bash
agentscribe delete session_20260614_1a2b3c4d
```

### 🖥️ 交互式仪表盘

```bash
# 启动交互式模式
agentscribe dashboard
```

---

## 💡 设计思路与迭代规划

### 设计理念

1. **本地优先** - 所有数据存储在本地 SQLite，无需网络，隐私安全
2. **CLI 原生** - 提供强大的命令行界面，适合开发者日常工作流
3. **模块化架构** - 存储、分析、报告各模块独立，易于扩展和二次开发
4. **开放格式** - 支持 JSON/Markdown/HTML 多种数据导出格式

### 技术架构

```
agentscribe/
├── agentscribe/          # 核心包
│   ├── cli.py            # CLI 入口（Click 框架）
│   ├── storage.py        # SQLite 存储引擎
│   ├── analyzer.py       # 分析引擎（成本/模式/统计）
│   ├── reporter.py       # HTML 报告生成器
│   ├── models.py         # 数据模型
│   ├── config.py         # 配置管理
│   └── utils.py          # 工具函数
├── tests/                # 单元测试
├── scripts/              # 安装脚本
├── setup.py              # 构建配置
└── requirements.txt      # 依赖管理
```

### 迭代规划

- **v0.2.0** - 自动代理会话嗅探（无需手动录制）
- **v0.3.0** - 跨会话模式识别与智能建议
- **v0.4.0** - 多用户/团队协作支持
- **v0.5.0** - Web 可视化仪表盘
- **v1.0.0** - 稳定版发布，插件生态

---

## 📦 打包与部署指南

### 构建发布包

```bash
# 安装构建工具
pip install build

# 构建源码和 wheel 包
python -m build

# 产物在 dist/ 目录
ls dist/
```

### 运行测试

```bash
# 安装测试依赖
pip install pytest flake8

# 运行所有测试
pytest tests/ -v

# 运行代码检查
flake8 agentscribe/
```

---

## 🤝 贡献指南

欢迎各种形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 贡献方式

- 🐛 **提交 Bug** - [创建 Issue](https://github.com/gitstq/agentscribe/issues/new?template=bug_report.md)
- 💡 **功能建议** - [提交 Feature Request](https://github.com/gitstq/agentscribe/issues/new?template=feature_request.md)
- 📝 **完善文档** - 帮助我们改进文档质量
- 🔧 **提交代码** - 提交 Pull Request 修复问题或添加功能

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源，您可以自由使用、修改和分发。

---

<p align="center">
  <b>AgentScribe</b> — 让 AI 编码代理的每一次交互都有迹可循 🚀
  <br>
  <a href="https://github.com/gitstq/agentscribe">GitHub</a> ·
  <a href="https://github.com/gitstq/agentscribe/issues">Issues</a> ·
  <a href="https://github.com/gitstq/agentscribe/releases">Releases</a>
</p>