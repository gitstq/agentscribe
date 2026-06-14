"""
AgentScribe - 工具函数模块
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List


def generate_session_id() -> str:
    """生成唯一会话ID"""
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    short_id = uuid.uuid4().hex[:8]
    return f"session_{ts}_{short_id}"


def timestamp_now() -> str:
    """获取当前时间戳"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_duration(ms: int) -> str:
    """格式化时长"""
    if ms < 1000:
        return f"{ms}ms"
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds / 60
    if minutes < 60:
        return f"{int(minutes)}m {int(seconds % 60)}s"
    hours = minutes / 60
    return f"{int(hours)}h {int(minutes % 60)}m"


def format_tokens(n: int) -> str:
    """格式化Token数量"""
    if n < 1000:
        return str(n)
    if n < 1_000_000:
        return f"{n / 1000:.1f}K"
    return f"{n / 1_000_000:.2f}M"


def truncate(text: str, max_len: int = 100) -> str:
    """截断文本"""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def detect_agent_from_env() -> Optional[str]:
    """从环境变量检测当前AI代理"""
    import os
    if os.environ.get("CLAUDE_CODE"):
        return "claude-code"
    if os.environ.get("CURSOR"):
        return "cursor"
    if os.environ.get("WINDSURF"):
        return "windsurf"
    if os.environ.get("GITHUB_COPILOT"):
        return "github-copilot"
    if os.environ.get("CODEX"):
        return "codex"
    return None


def load_json_file(path: str) -> Optional[dict]:
    """加载JSON文件"""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None