"""
AgentScribe - 数据模型模块
定义会话、消息、工具调用等核心数据结构
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import json


@dataclass
class AgentInfo:
    """AI代理信息"""
    name: str
    version: Optional[str] = None
    model: Optional[str] = None


@dataclass
class ToolCall:
    """工具调用记录"""
    tool_name: str
    input_preview: str
    output_preview: str
    duration_ms: int
    timestamp: str = ""


@dataclass
class SessionMessage:
    """会话中的单条消息"""
    role: str  # user, assistant, system
    content: str
    timestamp: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    tool_calls: list = field(default_factory=list)
    duration_ms: int = 0


@dataclass
class CodingSession:
    """完整的编码会话"""
    session_id: str
    agent: AgentInfo
    project_path: str
    start_time: str
    end_time: Optional[str] = None
    messages: list = field(default_factory=list)
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_cost: float = 0.0
    total_duration_ms: int = 0
    file_changes: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    summary: str = ""

    def to_dict(self):
        return asdict(self)

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)