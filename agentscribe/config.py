"""
AgentScribe - 配置管理模块
"""
import os
from pathlib import Path

# 默认配置
DEFAULT_CONFIG = {
    "storage_path": str(Path.home() / ".agentscribe" / "sessions.db"),
    "export_dir": str(Path.home() / ".agentscribe" / "exports"),
    "openai_api_key": "",
    "anthropic_api_key": "",
    "max_session_size_mb": 50,
    "auto_save_interval_sec": 60,
    "rich_theme": "default",
}


def get_config_dir() -> Path:
    """获取配置目录"""
    config_dir = Path.home() / ".agentscribe"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_storage_path() -> str:
    """获取数据库存储路径"""
    path = os.environ.get("AGENTSCRIBE_STORAGE")
    if path:
        return path
    return str(get_config_dir() / "sessions.db")


def get_export_dir() -> str:
    """获取导出目录"""
    path = os.environ.get("AGENTSCRIBE_EXPORT_DIR")
    if path:
        return path
    export_dir = get_config_dir() / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    return str(export_dir)