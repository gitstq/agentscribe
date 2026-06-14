"""
AgentScribe - 会话分析引擎
提供Token成本分析、模式识别、时间分布分析等功能
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import Counter, defaultdict

from .models import CodingSession, SessionMessage
from .storage import Storage


# 模型定价（每1K token，美元）
MODEL_PRICING = {
    "claude-3-opus": {"in": 0.015, "out": 0.075},
    "claude-3-sonnet": {"in": 0.003, "out": 0.015},
    "claude-3-haiku": {"in": 0.00025, "out": 0.00125},
    "claude-4-opus": {"in": 0.015, "out": 0.075},
    "claude-4-sonnet": {"in": 0.003, "out": 0.015},
    "gpt-4": {"in": 0.03, "out": 0.06},
    "gpt-4-turbo": {"in": 0.01, "out": 0.03},
    "gpt-4o": {"in": 0.005, "out": 0.015},
    "gpt-4o-mini": {"in": 0.00015, "out": 0.0006},
    "gpt-3.5-turbo": {"in": 0.0005, "out": 0.0015},
    "gpt-5": {"in": 0.01, "out": 0.04},
    "cursor-small": {"in": 0.0005, "out": 0.0015},
    "windsurf-default": {"in": 0.003, "out": 0.015},
    "deepseek-coder": {"in": 0.00014, "out": 0.00028},
    "default": {"in": 0.003, "out": 0.015},
}


class Analyzer:
    """会话分析引擎"""

    def __init__(self, storage: Storage):
        self.storage = storage

    @staticmethod
    def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
        """估算Token成本"""
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
        cost_in = (tokens_in / 1000) * pricing["in"]
        cost_out = (tokens_out / 1000) * pricing["out"]
        return round(cost_in + cost_out, 6)

    def analyze_session(self, session: CodingSession) -> Dict[str, Any]:
        """分析单个会话"""
        total_duration = session.total_duration_ms or 0
        msg_count = len(session.messages)
        user_msgs = sum(1 for m in session.messages if m.role == "user")
        assistant_msgs = sum(1 for m in session.messages if m.role == "assistant")

        tool_calls_count = sum(len(m.tool_calls) for m in session.messages)
        avg_response_time = total_duration / max(assistant_msgs, 1)

        # 工具使用频率
        tool_freq = Counter()
        for m in session.messages:
            for tc in m.tool_calls:
                tool_freq[tc.tool_name] += 1

        return {
            "session_id": session.session_id,
            "agent": session.agent.name,
            "model": session.agent.model,
            "duration_seconds": total_duration / 1000,
            "message_count": msg_count,
            "user_messages": user_msgs,
            "assistant_messages": assistant_msgs,
            "total_tokens_in": session.total_tokens_in,
            "total_tokens_out": session.total_tokens_out,
            "total_tokens": session.total_tokens_in + session.total_tokens_out,
            "estimated_cost": session.total_cost,
            "avg_tokens_per_message": (session.total_tokens_in + session.total_tokens_out) // max(msg_count, 1),
            "avg_response_time_ms": avg_response_time,
            "tool_calls_count": tool_calls_count,
            "top_tools": tool_freq.most_common(10),
            "summary": session.summary,
        }

    def weekly_report(self, days: int = 7) -> Dict[str, Any]:
        """生成周报"""
        sessions = self.storage.list_sessions(limit=1000)
        now = datetime.now()
        cutoff = now - timedelta(days=days)

        recent = [s for s in sessions if s.get("start_time", "") >= cutoff.isoformat()[:19]]

        total_sessions = len(recent)
        total_cost = sum(s.get("total_cost", 0) for s in recent)
        total_tokens = sum(s.get("total_tokens_in", 0) + s.get("total_tokens_out", 0) for s in recent)

        daily = defaultdict(lambda: {"count": 0, "cost": 0.0, "tokens": 0})
        for s in recent:
            day = s.get("start_time", "")[:10]
            daily[day]["count"] += 1
            daily[day]["cost"] += s.get("total_cost", 0)
            daily[day]["tokens"] += s.get("total_tokens_in", 0) + s.get("total_tokens_out", 0)

        return {
            "period_days": days,
            "total_sessions": total_sessions,
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "avg_cost_per_session": round(total_cost / max(total_sessions, 1), 6),
            "avg_tokens_per_session": total_tokens // max(total_sessions, 1),
            "daily_breakdown": dict(sorted(daily.items())),
        }

    def compare_agents(self) -> List[Dict]:
        """比较不同AI代理的使用情况"""
        stats = self.storage.get_stats()
        return stats.get("agent_breakdown", [])

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """粗略估算文本的token数量（中文约1.5字/token，英文约4字符/token）"""
        if not text:
            return 0
        char_count = len(text)
        # 简单估算：混合文本约2字符/token
        return max(1, char_count // 2)