"""
AgentScribe - HTML报告生成模块
生成美观的会话分析可视化报告
"""
import json
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .config import get_export_dir
from .analyzer import Analyzer
from .storage import Storage


class Reporter:
    """报告生成器"""

    REPORT_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AgentScribe 会话分析报告</title>
<style>
  :root {
    --primary: #6C5CE7;
    --primary-light: #A29BFE;
    --bg: #0F0F1A;
    --card-bg: #1A1A2E;
    --text: #E0E0F0;
    --text-muted: #8888AA;
    --border: #2A2A4A;
    --success: #00D2A0;
    --warning: #FFB347;
    --danger: #FF6B6B;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    padding: 0;
  }
  .header {
    background: linear-gradient(135deg, #6C5CE7 0%, #4834D4 50%, #2D1B69 100%);
    padding: 48px 32px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
    animation: pulse 8s ease-in-out infinite;
  }
  @keyframes pulse { 50% { transform: scale(1.1); } }
  .header h1 { font-size: 2.2em; margin-bottom: 8px; position: relative; }
  .header p { color: rgba(255,255,255,0.8); font-size: 1.1em; position: relative; }
  .container { max-width: 1200px; margin: 0 auto; padding: 32px 20px; }
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
  }
  .stat-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 32px rgba(108,92,231,0.2); }
  .stat-card .label { color: var(--text-muted); font-size: 0.9em; margin-bottom: 8px; }
  .stat-card .value { font-size: 1.8em; font-weight: 700; }
  .stat-card .sub { color: var(--text-muted); font-size: 0.8em; margin-top: 4px; }
  .card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 24px;
  }
  .card h2 { font-size: 1.3em; margin-bottom: 16px; color: var(--primary-light); }
  .card h3 { font-size: 1.1em; margin: 16px 0 8px; color: var(--text); }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th, td {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }
  th { color: var(--text-muted); font-weight: 600; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.5px; }
  tr:hover { background: rgba(108,92,231,0.05); }
  .tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.8em;
    margin: 2px;
  }
  .tag-ai { background: rgba(108,92,231,0.2); color: var(--primary-light); }
  .tag-tool { background: rgba(0,210,160,0.15); color: var(--success); }
  .tag-warn { background: rgba(255,179,71,0.15); color: var(--warning); }
  .progress-bar {
    height: 8px;
    background: var(--border);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 8px;
  }
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--primary), var(--primary-light));
    border-radius: 4px;
    transition: width 0.6s ease;
  }
  .footer {
    text-align: center;
    padding: 32px;
    color: var(--text-muted);
    font-size: 0.85em;
  }
  .badge { display: inline-flex; align-items: center; gap: 6px; }
  @media (max-width: 768px) {
    .header { padding: 32px 16px; }
    .header h1 { font-size: 1.6em; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
  }
</style>
</head>
<body>
<div class="header">
  <h1>📊 AgentScribe 会话分析报告</h1>
  <p>AI编码代理会话智能分析 · {date}</p>
</div>
<div class="container">
  <div class="stats-grid">
    <div class="stat-card">
      <div class="label">总会话数</div>
      <div class="value" style="color:var(--primary-light)">{total_sessions}</div>
      <div class="sub">所有AI代理</div>
    </div>
    <div class="stat-card">
      <div class="label">总Token消耗</div>
      <div class="value" style="color:var(--success)">{total_tokens:,}</div>
      <div class="sub">输入 + 输出</div>
    </div>
    <div class="stat-card">
      <div class="label">总成本</div>
      <div class="value" style="color:var(--warning)">${total_cost:.4f}</div>
      <div class="sub">按模型定价估算</div>
    </div>
    <div class="stat-card">
      <div class="label">总耗时</div>
      <div class="value" style="color:var(--danger)">{total_hours:.1f}h</div>
      <div class="sub">{total_minutes:.0f} 分钟</div>
    </div>
  </div>

  <div class="card">
    <h2>🤖 AI代理使用分布</h2>
    <table>
      <tr><th>代理名称</th><th>会话数</th><th>占比</th></tr>
      {agent_rows}
    </table>
  </div>

  <div class="card">
    <h2>📋 最近会话</h2>
    <table>
      <tr><th>会话ID</th><th>代理</th><th>模型</th><th>Token数</th><th>成本</th><th>时间</th></tr>
      {session_rows}
    </table>
  </div>

  <div class="card">
    <h2>💡 使用建议</h2>
    <ul style="padding-left: 20px; line-height: 2;">
      <li>📈 您的AI编码代理使用频率为 <strong>{sessions_per_day:.1f}</strong> 次/天</li>
      <li>💰 日均成本约 <strong>${daily_cost:.4f}</strong></li>
      <li>⚡ 考虑使用更经济的模型减少 <strong>{cost_saving_tokens:,}</strong> Token的高频会话成本</li>
      <li>🔄 定期清理长时间未使用的会话记录</li>
    </ul>
  </div>
</div>
<div class="footer">
  <p>AgentScribe v0.1.0 · 报告生成于 {generate_time} · 数据本地存储，隐私无忧</p>
</div>
</body>
</html>"""

    def __init__(self, storage: Storage):
        self.storage = storage
        self.analyzer = Analyzer(storage)

    def generate_report(self, output_path: Optional[str] = None,
                        days: int = 30) -> str:
        """生成HTML分析报告"""
        stats = self.storage.get_stats()
        sessions = self.storage.list_sessions(limit=50)

        total_sessions = stats["total_sessions"]
        total_tokens_in = stats["total_tokens_in"]
        total_tokens_out = stats["total_tokens_out"]
        total_tokens = total_tokens_in + total_tokens_out
        total_cost = stats["total_cost"]
        total_duration_ms = stats["total_duration_ms"]
        total_hours = total_duration_ms / 3600000
        total_minutes = total_duration_ms / 60000

        # 代理分布行
        agent_rows = ""
        for a in stats.get("agent_breakdown", []):
            pct = (a["count"] / max(total_sessions, 1)) * 100
            agent_rows += f"<tr><td><span class='badge'><span class='tag tag-ai'>{a['agent_name']}</span></td><td>{a['count']}</td><td>{pct:.1f}%</td></tr>\n"

        # 会话行
        session_rows = ""
        for s in sessions[:20]:
            tokens = (s.get("total_tokens_in", 0) or 0) + (s.get("total_tokens_out", 0) or 0)
            cost = s.get("total_cost", 0) or 0
            sid = s["session_id"][:12] + "..." if len(s.get("session_id", "")) > 15 else s.get("session_id", "N/A")
            model = s.get("agent_model", "") or "N/A"
            start = (s.get("start_time", "") or "")[:16]
            session_rows += f"<tr><td style='font-family:monospace;font-size:0.85em'>{sid}</td><td>{s.get('agent_name', '')}</td><td><span class='tag tag-tool'>{model}</span></td><td>{tokens:,}</td><td>${cost:.4f}</td><td>{start}</td></tr>\n"

        now = datetime.now()
        sessions_per_day = total_sessions / max(days, 1)
        daily_cost = total_cost / max(days, 1)
        cost_saving_tokens = total_tokens_in // 2

        report_html = self.REPORT_TEMPLATE.format(
            date=now.strftime("%Y-%m-%d %H:%M"),
            generate_time=now.strftime("%Y-%m-%d %H:%M"),
            total_sessions=total_sessions,
            total_tokens=total_tokens,
            total_cost=total_cost,
            total_hours=total_hours,
            total_minutes=total_minutes,
            agent_rows=agent_rows,
            session_rows=session_rows,
            sessions_per_day=sessions_per_day,
            daily_cost=daily_cost,
            cost_saving_tokens=cost_saving_tokens,
        )

        if output_path:
            path = Path(output_path)
        else:
            export_dir = Path(get_export_dir())
            export_dir.mkdir(parents=True, exist_ok=True)
            path = export_dir / f"agentscribe_report_{now.strftime('%Y%m%d_%H%M%S')}.html"

        path.write_text(report_html, encoding="utf-8")
        return str(path)

    def open_report(self, report_path: str):
        """在浏览器中打开报告"""
        webbrowser.open(f"file://{Path(report_path).resolve()}")