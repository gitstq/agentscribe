"""AgentScribe 单元测试 - 分析引擎"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agentscribe.analyzer import Analyzer
from agentscribe.storage import Storage
from agentscribe.models import CodingSession, AgentInfo, SessionMessage, ToolCall


def test_estimate_cost():
    """测试成本估算"""
    # Claude-4-Sonnet
    cost = Analyzer.estimate_cost("claude-4-sonnet", 1000, 2000)
    assert cost > 0
    assert isinstance(cost, float)

    # GPT-4o
    cost = Analyzer.estimate_cost("gpt-4o", 1000, 1000)
    assert cost > 0

    # Unknown model uses default pricing
    cost = Analyzer.estimate_cost("unknown-model", 1000, 1000)
    assert cost > 0

    # Zero tokens should cost 0
    cost = Analyzer.estimate_cost("gpt-4o", 0, 0)
    assert cost == 0


def test_estimate_tokens():
    """测试Token估算"""
    assert Analyzer.estimate_tokens("") == 0
    assert Analyzer.estimate_tokens("hello world") == 5  # 11 chars // 2
    assert Analyzer.estimate_tokens("你好世界") == 2  # 4 chars // 2


def test_analyze_session():
    """测试会话分析"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        storage = Storage(db_path)
        analyzer = Analyzer(storage)

        session = CodingSession(
            session_id="test_analyze",
            agent=AgentInfo(name="claude-code", model="claude-4-sonnet"),
            project_path="/test",
            start_time="2026-06-14 10:00:00",
            end_time="2026-06-14 10:30:00",
            total_tokens_in=5000,
            total_tokens_out=12000,
            total_cost=0.045,
            total_duration_ms=1800000,
            messages=[
                SessionMessage(role="user", content="Hello", tokens_in=100),
                SessionMessage(
                    role="assistant", content="Hi there!", tokens_in=100, tokens_out=200,
                    tool_calls=[ToolCall(tool_name="Read", input_preview="file.py", output_preview="code", duration_ms=300)]
                ),
            ],
        )
        storage.save_session(session)

        result = analyzer.analyze_session(session)
        assert result["session_id"] == "test_analyze"
        assert result["total_tokens"] == 17000
        assert result["message_count"] == 2
        assert result["tool_calls_count"] == 1
        assert result["top_tools"][0][0] == "Read"
    finally:
        os.unlink(db_path)


def test_weekly_report():
    """测试周报生成"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        storage = Storage(db_path)
        analyzer = Analyzer(storage)

        session = CodingSession(
            session_id="test_weekly",
            agent=AgentInfo(name="cursor"),
            project_path="/test",
            start_time="2026-06-14 10:00:00",
            total_tokens_in=1000,
            total_tokens_out=2000,
            total_cost=0.01,
            total_duration_ms=60000,
        )
        storage.save_session(session)

        report = analyzer.weekly_report(days=7)
        assert "total_sessions" in report
        assert "total_cost" in report
        assert "total_tokens" in report
    finally:
        os.unlink(db_path)


if __name__ == "__main__":
    test_estimate_cost()
    test_estimate_tokens()
    test_analyze_session()
    test_weekly_report()
    print("✅ 所有分析引擎测试通过!")