# 📊 AgentScribe

> **AI Coding Agent Session Recorder & Analytics Tool**
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

## 🎉 Introduction

**AgentScribe** is a **session recording and analytics tool** designed for AI coding agents. It records, replays, and analyzes your interactions with AI coding agents (such as Claude Code, Cursor, Windsurf, GitHub Copilot, Codex, and more), helping you to:

- 📈 **Understand Agent Behavior** - Track decision processes and tool calls in every session
- 💰 **Optimize Token Costs** - Count token consumption, estimate usage costs
- 🔍 **Retrospective Sessions** - Quickly search and replay past coding sessions
- 📊 **Generate Analytics Reports** - Output beautiful HTML visualization reports
- 🧠 **Discover Usage Patterns** - Identify high-frequency tool calls and coding patterns

> **Design Philosophy:** Local-first, data privacy paramount. All session data is stored in your local SQLite database — no network required, no data leakage risk.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎬 **Session Recording** | Interactively record complete AI coding agent sessions including user messages, AI responses, and tool calls |
| 📋 **Session List** | Browse historical sessions by time, agent, model, and more |
| 🔍 **Detail View** | Dive into each message's content, token consumption, and tool call details |
| 📊 **Global Statistics** | Aggregate token, cost, and duration statistics across all sessions |
| 📈 **HTML Reports** | Generate beautiful interactive HTML analytics reports for sharing and archiving |
| 💾 **Data Export** | Export sessions in JSON and Markdown formats |
| 🤖 **Multi-Agent Support** | Compatible with Claude Code, Cursor, Windsurf, GitHub Copilot, Codex and more |
| 🖥️ **Interactive Dashboard** | Built-in interactive CLI dashboard for one-stop session management |
| 🏷️ **Tag System** | Add custom tags to sessions for easy categorization and retrieval |
| 🧹 **Data Management** | Session deletion and batch cleanup functionality |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip (Python package manager)

### One-Click Install

```bash
# Option 1: pip install (recommended)
pip install agentscribe

# Option 2: Install from source
git clone https://github.com/gitstq/agentscribe.git
cd agentscribe
pip install -e .

# Option 3: Use install script
chmod +x scripts/install.sh
./scripts/install.sh
```

### Verify Installation

```bash
agentscribe --version
agentscribe --help
```

---

## 📖 Usage Guide

### 📋 List Sessions

```bash
# List recent 20 sessions
agentscribe list

# Filter by specific agent
agentscribe list --agent claude-code

# JSON format output
agentscribe list --json
```

### 🎬 Record a New Session

```bash
# Interactive recording
agentscribe record

# Specify agent and model
agentscribe record --agent cursor --model gpt-4o --project /path/to/project

# Add tags
agentscribe record --tag frontend --tag refactor
```

### 🔍 View Session Details

```bash
# View specific session details
agentscribe view session_20260614_1a2b3c4d

# JSON format output
agentscribe view session_20260614_1a2b3c4d --json
```

### 📊 View Statistics

```bash
# View global statistics
agentscribe stats
```

### 📈 Generate Report

```bash
# Generate HTML analytics report
agentscribe report

# Specify output path and auto-open
agentscribe report --output ./report.html --open
```

### 💾 Export Session

```bash
# Export as JSON
agentscribe export session_20260614_1a2b3c4d

# Export as Markdown
agentscribe export session_20260614_1a2b3c4d --format markdown
```

### 🗑️ Delete Session

```bash
agentscribe delete session_20260614_1a2b3c4d
```

### 🖥️ Interactive Dashboard

```bash
# Start interactive mode
agentscribe dashboard
```

---

## 💡 Design Philosophy & Roadmap

### Design Principles

1. **Local-First** - All data stored in local SQLite, no network required, privacy secure
2. **CLI Native** - Powerful command-line interface suitable for developer daily workflow
3. **Modular Architecture** - Storage, analysis, and reporting modules are independent and extensible
4. **Open Formats** - Support JSON/Markdown/HTML multiple data export formats

### Architecture

```
agentscribe/
├── agentscribe/          # Core package
│   ├── cli.py            # CLI entry point (Click framework)
│   ├── storage.py        # SQLite storage engine
│   ├── analyzer.py       # Analysis engine (cost/pattern/stats)
│   ├── reporter.py       # HTML report generator
│   ├── models.py         # Data models
│   ├── config.py         # Configuration management
│   └── utils.py          # Utility functions
├── tests/                # Unit tests
├── scripts/              # Install scripts
├── setup.py              # Build configuration
└── requirements.txt      # Dependency management
```

### Roadmap

- **v0.2.0** - Automatic agent session sniffing (no manual recording)
- **v0.3.0** - Cross-session pattern recognition and smart suggestions
- **v0.4.0** - Multi-user/team collaboration support
- **v0.5.0** - Web visualization dashboard
- **v1.0.0** - Stable release, plugin ecosystem

---

## 📦 Build & Deploy

### Build Distribution Package

```bash
# Install build tools
pip install build

# Build source and wheel packages
python -m build

# Artifacts in dist/
ls dist/
```

### Run Tests

```bash
# Install test dependencies
pip install pytest flake8

# Run all tests
pytest tests/ -v

# Run code linting
flake8 agentscribe/
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

- 🐛 **Report Bugs** - [Create an Issue](https://github.com/gitstq/agentscribe/issues/new?template=bug_report.md)
- 💡 **Feature Requests** - [Submit a Feature Request](https://github.com/gitstq/agentscribe/issues/new?template=feature_request.md)
- 📝 **Improve Docs** - Help us improve documentation quality
- 🔧 **Submit Code** - Submit a Pull Request to fix issues or add features

---

## 📄 License

This project is open-sourced under the [MIT License](LICENSE).

---

<p align="center">
  <b>AgentScribe</b> — Make every AI coding agent interaction traceable 🚀
  <br>
  <a href="https://github.com/gitstq/agentscribe">GitHub</a> ·
  <a href="https://github.com/gitstq/agentscribe/issues">Issues</a> ·
  <a href="https://github.com/gitstq/agentscribe/releases">Releases</a>
</p>