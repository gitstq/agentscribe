"""
AgentScribe - 存储引擎模块
基于SQLite的本地会话存储，支持增删改查和统计分析
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .config import get_storage_path, get_export_dir
from .models import CodingSession, SessionMessage, ToolCall, AgentInfo


class Storage:
    """会话存储引擎"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or get_storage_path()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self):
        """初始化数据库表结构"""
        conn = self._get_conn()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    agent_version TEXT,
                    agent_model TEXT,
                    project_path TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    total_tokens_in INTEGER DEFAULT 0,
                    total_tokens_out INTEGER DEFAULT 0,
                    total_cost REAL DEFAULT 0.0,
                    total_duration_ms INTEGER DEFAULT 0,
                    summary TEXT DEFAULT '',
                    tags TEXT DEFAULT '[]',
                    created_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT,
                    timestamp TEXT,
                    tokens_in INTEGER DEFAULT 0,
                    tokens_out INTEGER DEFAULT 0,
                    duration_ms INTEGER DEFAULT 0,
                    tool_calls TEXT DEFAULT '[]',
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS file_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    change_type TEXT DEFAULT 'modified',
                    diff_preview TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    session_count INTEGER DEFAULT 0,
                    total_tokens_in INTEGER DEFAULT 0,
                    total_tokens_out INTEGER DEFAULT 0,
                    total_cost REAL DEFAULT 0.0,
                    total_duration_ms INTEGER DEFAULT 0
                );

                CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
                CREATE INDEX IF NOT EXISTS idx_file_changes_session ON file_changes(session_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_start ON sessions(start_time);
            """)
            conn.commit()
        finally:
            conn.close()

    def save_session(self, session: CodingSession) -> str:
        """保存会话记录"""
        conn = self._get_conn()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO sessions
                (session_id, agent_name, agent_version, agent_model, project_path,
                 start_time, end_time, total_tokens_in, total_tokens_out,
                 total_cost, total_duration_ms, summary, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.agent.name,
                session.agent.version,
                session.agent.model,
                session.project_path,
                session.start_time,
                session.end_time,
                session.total_tokens_in,
                session.total_tokens_out,
                session.total_cost,
                session.total_duration_ms,
                session.summary,
                json.dumps(session.tags, ensure_ascii=False),
            ))

            # 批量插入消息
            for msg in session.messages:
                conn.execute("""
                    INSERT INTO messages
                    (session_id, role, content, timestamp, tokens_in, tokens_out, duration_ms, tool_calls)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id, msg.role, msg.content[:10000] if msg.content else "",
                    msg.timestamp, msg.tokens_in, msg.tokens_out, msg.duration_ms,
                    json.dumps([asdict(tc) for tc in msg.tool_calls], ensure_ascii=False) if msg.tool_calls else '[]',
                ))

            conn.commit()
            return session.session_id
        finally:
            conn.close()

    def get_session(self, session_id: str) -> Optional[CodingSession]:
        """获取单个会话详情"""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if not row:
                return None

            session = self._row_to_session(row)

            # 获取消息
            msg_rows = conn.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY id", (session_id,)
            ).fetchall()

            for mr in msg_rows:
                msg = SessionMessage(
                    role=mr["role"],
                    content=mr["content"],
                    timestamp=mr["timestamp"],
                    tokens_in=mr["tokens_in"],
                    tokens_out=mr["tokens_out"],
                    duration_ms=mr["duration_ms"],
                    tool_calls=[ToolCall(**tc) for tc in json.loads(mr["tool_calls"] or "[]")],
                )
                session.messages.append(msg)

            return session
        finally:
            conn.close()

    def list_sessions(self, limit: int = 50, offset: int = 0,
                      agent: Optional[str] = None, sort_by: str = "start_time") -> List[Dict]:
        """列出会话摘要"""
        conn = self._get_conn()
        try:
            where = ""
            params = []
            if agent:
                where = "WHERE agent_name = ?"
                params.append(agent)

            order = "DESC" if sort_by == "start_time" else "DESC"
            rows = conn.execute(f"""
                SELECT session_id, agent_name, agent_model, project_path,
                       start_time, end_time, total_tokens_in, total_tokens_out,
                       total_cost, total_duration_ms, summary, tags
                FROM sessions {where}
                ORDER BY start_time {order}
                LIMIT ? OFFSET ?
            """, (*params, limit, offset)).fetchall()

            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """获取全局统计信息"""
        conn = self._get_conn()
        try:
            stats = conn.execute("""
                SELECT
                    COUNT(*) as total_sessions,
                    COALESCE(SUM(total_tokens_in), 0) as total_tokens_in,
                    COALESCE(SUM(total_tokens_out), 0) as total_tokens_out,
                    COALESCE(SUM(total_cost), 0) as total_cost,
                    COALESCE(SUM(total_duration_ms), 0) as total_duration_ms
                FROM sessions
            """).fetchone()

            agent_stats = conn.execute("""
                SELECT agent_name, COUNT(*) as count,
                       COALESCE(AVG(total_cost), 0) as avg_cost
                FROM sessions GROUP BY agent_name ORDER BY count DESC
            """).fetchall()

            daily = conn.execute("""
                SELECT date, session_count, total_cost
                FROM daily_stats ORDER BY date DESC LIMIT 30
            """).fetchall()

            return {
                "total_sessions": stats["total_sessions"],
                "total_tokens_in": stats["total_tokens_in"],
                "total_tokens_out": stats["total_tokens_out"],
                "total_cost": stats["total_cost"],
                "total_duration_ms": stats["total_duration_ms"],
                "agent_breakdown": [dict(a) for a in agent_stats],
                "daily_stats": [dict(d) for d in daily],
            }
        finally:
            conn.close()

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()

    def export_session(self, session_id: str, fmt: str = "json") -> Optional[str]:
        """导出会话到文件"""
        session = self.get_session(session_id)
        if not session:
            return None

        export_dir = Path(get_export_dir())
        export_dir.mkdir(parents=True, exist_ok=True)

        if fmt == "json":
            path = export_dir / f"session_{session_id}.json"
            path.write_text(session.to_json(), encoding="utf-8")
        elif fmt == "markdown":
            path = export_dir / f"session_{session_id}.md"
            path.write_text(self._to_markdown(session), encoding="utf-8")
        else:
            return None

        return str(path)

    def _row_to_session(self, row) -> CodingSession:
        return CodingSession(
            session_id=row["session_id"],
            agent=AgentInfo(
                name=row["agent_name"],
                version=row["agent_version"],
                model=row["agent_model"],
            ),
            project_path=row["project_path"] or "",
            start_time=row["start_time"],
            end_time=row["end_time"],
            total_tokens_in=row["total_tokens_in"],
            total_tokens_out=row["total_tokens_out"],
            total_cost=row["total_cost"],
            total_duration_ms=row["total_duration_ms"],
            summary=row["summary"] or "",
            tags=json.loads(row["tags"] or "[]"),
        )

    def _to_markdown(self, session: CodingSession) -> str:
        lines = [
            f"# Session: {session.session_id}",
            f"",
            f"**Agent**: {session.agent.name} ({session.agent.model or 'N/A'})",
            f"**Project**: {session.project_path}",
            f"**Duration**: {session.total_duration_ms / 1000:.1f}s",
            f"**Tokens**: {session.total_tokens_in} in / {session.total_tokens_out} out",
            f"**Cost**: ${session.total_cost:.4f}",
            f"",
            f"## Messages ({len(session.messages)})",
            f"",
        ]
        for i, msg in enumerate(session.messages, 1):
            lines.append(f"### {i}. [{msg.role}]")
            if msg.content:
                lines.append(f"```\n{msg.content[:500]}\n```")
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    lines.append(f"- Tool: `{tc.tool_name}` ({tc.duration_ms}ms)")
            lines.append("")
        return "\n".join(lines)


# 辅助函数，避免循环导入
def asdict(obj):
    """将dataclass转换为dict"""
    if hasattr(obj, '__dataclass_fields__'):
        result = {}
        for field_name in obj.__dataclass_fields__:
            value = getattr(obj, field_name)
            if hasattr(value, '__dataclass_fields__'):
                result[field_name] = asdict(value)
            elif isinstance(value, list):
                result[field_name] = [asdict(item) if hasattr(item, '__dataclass_fields__') else item for item in value]
            else:
                result[field_name] = value
        return result
    return obj