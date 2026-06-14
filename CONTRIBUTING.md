# AgentScribe

> 欢迎提交 Issue 和 Pull Request 来帮助改进 AgentScribe！

## 如何贡献

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的改动 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 开发指南

```bash
# 克隆仓库
git clone https://github.com/gitstq/agentscribe.git
cd agentscribe

# 安装开发依赖
pip install -e ".[dev]" --break-system-packages

# 运行测试
pytest tests/ -v

# 运行代码检查
flake8 agentscribe/
```

## 提交规范

我们使用 [Angular Commit Convention](https://www.conventionalcommits.org/):

- `feat:` 新功能
- `fix:` 修复
- `docs:` 文档
- `style:` 代码风格
- `refactor:` 重构
- `test:` 测试
- `chore:` 构建/工具

## 行为准则

请保持友善和尊重。我们致力于为所有贡献者创造一个友好的环境。