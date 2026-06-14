"""AgentScribe 单元测试 - 存储引擎"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agentscribe.storage import Storage
from agentscribe.models import CodingSession, AgentInfo, SessionMessage, ToolCall


def test_storage_init():
    """测试数据库初始化"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        storage = Storage(db_path)
        assert os.path.exists(db_path)
        # 验证表已创建
        conn = storage._get_conn()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t["name"] for t in tables if t["name"] != "sqlite_sequence"]
        assert "sessions" in table_names
        assert "messages" in table_names
        assert "file_changes" in table_names
        assert "daily_stats" in table_names
        conn.close()
    finally:
        os.unlink(db_path)


def test_save_and_get_session():
    """测试保存和获取会话"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        storage = Storage(db_path)

        session = CodingSession(
            session_id="test_session_001",
            agent=AgentInfo(name="claude-code", version="1.0", model="claude-4-sonnet"),
            project_path="/home/user/project",
            start_time="2026-06-14 10:00:00",
            end_time="2026-06-14 10:30:00",
            total_tokens_in=5000,
            total_tokens_out=12000,
            total_cost=0.045,
            total_duration_ms=1800000,
            summary="测试会话",
            tags=["test", "demo"],
            messages=[
                SessionMessage(
                    role="user",
                    content="Hello, please refactor this code",
                    timestamp="2026-06-14 10:00:05",
                    tokens_in=50,
                ),
                SessionMessage(
                    role="assistant",
                    content="Sure, I'll refactor the code for you.",
                    timestamp="2026-06-14 10:00:10",
                    tokens_in=50,
                    tokens_out=200,
                    tool_calls=[
                        ToolCall(
                            tool_name="Read",
                            input_preview="src/main.py",
                            output_preview="def main():...",
                            duration_ms=500,
                        )
                    ],
                ),
            ],
        )

        saved_id = storage.save_session(session)
        assert saved_id == "test_session_001"

        loaded = storage.get_session("test_session_001")
        assert loaded is not None
        assert loaded.session_id == "test_session_001"
        assert loaded.agent.name == "claude-code"
        assert loaded.agent.model == "claude-4-sonnet"
        assert len(loaded.messages) == 2
        assert loaded.messages[0].role == "user"
        assert loaded.messages[1].role == "assistant"
        assert len(loaded.messages[1].tool_calls) == 1

        # 测试列表
        sessions = storage.list_sessions()
        assert len(sessions) >= 1
        assert sessions[0]["session_id"] == "test_session_001"
    finally:
        os.unlink(db_path)


def test_delete_session():
    """测试删除会话"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        storage = Storage(db_path)

        session = CodingSession(
            session_id="test_delete",
            agent=AgentInfo(name="cursor"),
            project_path="/test",
            start_time="2026-06-14 10:00:00",
        )
        storage.save_session(session)

        assert storage.get_session("test_delete") is not None
        assert storage.delete_session("test_delete") is True
        assert storage.get_session("test_delete") is None
        assert storage.delete_session("nonexistent") is False
    finally:
        os.unlink(db_path)


def test_get_stats():
    """测试全局统计"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        storage = Storage(db_path)

        # 保存两个会话
        for i in range(2):
            session = CodingSession(
                session_id=f"test_stats_{i}",
                agent=AgentInfo(name="claude-code"),
                project_path="/test",
                start_time=f"2026-06-{13+i} 10:00:00",
                total_tokens_in=1000 * (i + 1),
                total_tokens_out=2000 * (i + 1),
                total_cost=0.01 * (i + 1),
                total_duration_ms=60000 * (i + 1),
            )
            storage.save_session(session)

        stats = storage.get_stats()
        assert stats["total_sessions"] == 2
        assert stats["total_tokens_in"] == 3000  # 1000 + 2000
        assert stats["total_tokens_out"] == 6000  # 2000 + 4000
        assert stats["total_cost"] == 0.03  # 0.01 + 0.02
    finally:
        os.unlink(db_path)


if __name__ == "__main__":
    test_storage_init()
    test_save_and_get_session()
    test_delete_session()
    test_get_stats()
    print("✅ 所有存储引擎测试通过!")