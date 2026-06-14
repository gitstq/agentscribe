"""
AgentScribe - 命令行界面模块
提供完整的CLI交互界面，支持会话管理、分析、导出等功能
"""
import sys
from pathlib import Path
from typing import Optional

import click

from . import __version__
from .storage import Storage
from .analyzer import Analyzer
from .reporter import Reporter
from .models import CodingSession, AgentInfo, SessionMessage, ToolCall
from .utils import generate_session_id, timestamp_now, format_duration, format_tokens, truncate


# 全局样式常量
STYLE_PRIMARY = "bold purple"
STYLE_SUCCESS = "bold green"
STYLE_WARN = "bold yellow"
STYLE_INFO = "bold cyan"
STYLE_TITLE = "bold white"


@click.group()
@click.version_option(version=__version__, prog_name="AgentScribe")
@click.option("--db", envvar="AGENTSCRIBE_DB", help="数据库路径", default=None)
@click.pass_context
def cli(ctx, db):
    """📊 AgentScribe - AI编码代理会话记录与智能分析工具

    记录、分析和可视化AI编码代理（Claude Code、Cursor、Windsurf等）的会话数据。
    """
    ctx.ensure_object(dict)
    ctx.obj["storage"] = Storage(db)
    ctx.obj["analyzer"] = Analyzer(ctx.obj["storage"])
    ctx.obj["reporter"] = Reporter(ctx.obj["storage"])


# ============ 记录命令 ============

@cli.command()
@click.option("--agent", "-a", default="unknown", help="AI代理名称")
@click.option("--model", "-m", default=None, help="AI模型名称")
@click.option("--project", "-p", default=".", help="项目路径")
@click.option("--tag", "-t", multiple=True, help="会话标签")
@click.pass_context
def record(ctx, agent, model, project, tag):
    """🎬 开始录制新会话"""
    storage = ctx.obj["storage"]
    project_path = str(Path(project).resolve())

    session = CodingSession(
        session_id=generate_session_id(),
        agent=AgentInfo(name=agent, model=model),
        project_path=project_path,
        start_time=timestamp_now(),
        tags=list(tag),
    )

    click.echo(f"\n{'='*50}")
    click.echo(f"  🎬 AgentScribe 会话录制")
    click.echo(f"{'='*50}")
    click.echo(f"  📋 会话ID: {session.session_id}")
    click.echo(f"  🤖 代理:     {agent}")
    click.echo(f"  📁 项目:     {project_path}")
    click.echo(f"{'='*50}\n")

    click.echo("  输入消息 (输入空行结束，输入 '--summary <text>' 设置摘要):\n")

    total_tokens_in = 0
    total_tokens_out = 0
    total_cost = 0.0

    while True:
        line = click.prompt("  👤 User", default="", show_default=False)
        if not line:
            break

        if line.startswith("--summary "):
            session.summary = line[10:]
            click.echo(f"  ✅ 摘要已设置: {truncate(session.summary, 60)}\n")
            continue

        if line.startswith("--tool "):
            parts = line[7:].split("|", 3)
            if len(parts) >= 2:
                tc = ToolCall(
                    tool_name=parts[0].strip(),
                    input_preview=truncate(parts[1].strip(), 100),
                    output_preview=truncate(parts[2].strip(), 100) if len(parts) > 2 else "",
                    duration_ms=0,
                    timestamp=timestamp_now(),
                )
                # We'd normally add to last message, simplified here
                click.echo(f"  🛠️  工具调用记录: {tc.tool_name}\n")
            continue

        # 估算token
        estimated_tokens = len(line) // 2
        total_tokens_in += estimated_tokens

        msg = SessionMessage(
            role="user",
            content=line,
            timestamp=timestamp_now(),
            tokens_in=estimated_tokens,
        )
        session.messages.append(msg)

        # 模拟助理回复
        reply = click.prompt("  🤖 Assistant", default="", show_default=False)
        if reply:
            out_tokens = len(reply) // 2
            total_tokens_out += out_tokens
            total_tokens_in += estimated_tokens  # assistant输入就是上下文

            assistant_msg = SessionMessage(
                role="assistant",
                content=reply,
                timestamp=timestamp_now(),
                tokens_in=estimated_tokens,
                tokens_out=out_tokens,
            )
            session.messages.append(assistant_msg)

        click.echo("")

    # 更新会话统计
    session.total_tokens_in = total_tokens_in
    session.total_tokens_out = total_tokens_out
    session.end_time = timestamp_now()

    # 成本估算
    model = model or "default"
    from .analyzer import Analyzer
    session.total_cost = Analyzer.estimate_cost(model, total_tokens_in, total_tokens_out)

    # 保存
    storage.save_session(session)

    click.echo(f"\n{'='*50}")
    click.echo(f"  ✅ 会话已保存!")
    click.echo(f"  📋 会话ID: {session.session_id}")
    click.echo(f"  🗣️  消息数: {len(session.messages)}")
    click.echo(f"  📊 Token:   {format_tokens(total_tokens_in)} in / {format_tokens(total_tokens_out)} out")
    click.echo(f"  💰 成本:    ${session.total_cost:.6f}")
    click.echo(f"{'='*50}\n")


# ============ 列表命令 ============

@cli.command()
@click.option("--limit", "-l", default=20, help="显示数量")
@click.option("--agent", "-a", default=None, help="按代理筛选")
@click.option("--json", "as_json", is_flag=True, help="JSON格式输出")
@click.pass_context
def list(ctx, limit, agent, as_json):
    """📋 列出会话记录"""
    storage = ctx.obj["storage"]
    sessions = storage.list_sessions(limit=limit, agent=agent)

    if not sessions:
        click.echo("\n  📭 暂无会话记录\n")
        return

    if as_json:
        import json as j
        click.echo(j.dumps(sessions, ensure_ascii=False, indent=2))
        return

    click.echo(f"\n{'='*80}")
    click.echo(f"  📋 最近会话记录 ({len(sessions)} 条)")
    click.echo(f"{'='*80}")
    click.echo(f"  {'ID':<22} {'代理':<14} {'模型':<18} {'Token':<12} {'成本':<10} {'时间'}")
    click.echo(f"  {'-'*78}")

    for s in sessions:
        sid = s["session_id"][:20] if s.get("session_id") else "N/A"
        agent_name = s.get("agent_name", "?")[:12]
        model = (s.get("agent_model") or "N/A")[:16]
        tokens = (s.get("total_tokens_in", 0) or 0) + (s.get("total_tokens_out", 0) or 0)
        cost = s.get("total_cost", 0) or 0
        start = (s.get("start_time") or "")[:16]
        click.echo(f"  {sid:<22} {agent_name:<14} {model:<18} {format_tokens(tokens):<12} ${cost:<8.4f} {start}")

    click.echo(f"{'='*80}\n")


# ============ 查看详情命令 ============

@cli.command()
@click.argument("session_id")
@click.option("--json", "as_json", is_flag=True, help="JSON格式输出")
@click.pass_context
def view(ctx, session_id, as_json):
    """🔍 查看会话详情"""
    storage = ctx.obj["storage"]
    session = storage.get_session(session_id)

    if not session:
        click.echo(f"\n  ❌ 未找到会话: {session_id}\n")
        return

    if as_json:
        click.echo(session.to_json())
        return

    click.echo(f"\n{'='*60}")
    click.echo(f"  🔍 会话详情")
    click.echo(f"{'='*60}")
    click.echo(f"  📋 ID:       {session.session_id}")
    click.echo(f"  🤖 代理:     {session.agent.name}")
    click.echo(f"  🏷️  模型:     {session.agent.model or 'N/A'}")
    click.echo(f"  📁 项目:     {session.project_path}")
    click.echo(f"  🕐 开始:     {session.start_time}")
    click.echo(f"  🕐 结束:     {session.end_time or '进行中'}")
    click.echo(f"  📊 Token:    {format_tokens(session.total_tokens_in)} in / {format_tokens(session.total_tokens_out)} out")
    click.echo(f"  💰 成本:     ${session.total_cost:.6f}")
    click.echo(f"  ⏱️  时长:     {format_duration(session.total_duration_ms)}")
    click.echo(f"  🗣️  消息数:   {len(session.messages)}")
    click.echo(f"  📝 摘要:     {truncate(session.summary, 80) if session.summary else '无'}")

    if session.messages:
        click.echo(f"\n{'─'*60}")
        click.echo(f"  消息记录:")
        click.echo(f"{'─'*60}")
        for i, msg in enumerate(session.messages[-10:], max(1, len(session.messages) - 9)):
            role_icon = "👤" if msg.role == "user" else "🤖"
            click.echo(f"\n  {role_icon} [{msg.role}] ({format_tokens(msg.tokens_in + msg.tokens_out)})")
            if msg.content:
                content_preview = truncate(msg.content, 200)
                click.echo(f"  {content_preview}")
            if msg.tool_calls:
                for tc in msg.tool_calls[:3]:
                    click.echo(f"  🛠️  → {tc.tool_name} ({tc.duration_ms}ms)")

    click.echo(f"\n{'='*60}\n")


# ============ 统计命令 ============

@cli.command()
@click.pass_context
def stats(ctx):
    """📊 查看全局统计"""
    storage = ctx.obj["storage"]
    stats = storage.get_stats()
    analyzer = ctx.obj["analyzer"]

    click.echo(f"\n{'='*50}")
    click.echo(f"  📊 AgentScribe 全局统计")
    click.echo(f"{'='*50}")
    click.echo(f"  总会话数:     {stats['total_sessions']}")
    click.echo(f"  总Token输入:  {format_tokens(stats['total_tokens_in'])}")
    click.echo(f"  总Token输出:  {format_tokens(stats['total_tokens_out'])}")
    click.echo(f"  总成本:       ${stats['total_cost']:.4f}")
    click.echo(f"  总耗时:       {format_duration(stats['total_duration_ms'])}")
    click.echo("")

    agent_breakdown = stats.get("agent_breakdown", [])
    if agent_breakdown:
        click.echo(f"  🤖 代理使用分布:")
        for a in agent_breakdown:
            pct = (a["count"] / max(stats["total_sessions"], 1)) * 100
            bar_len = max(1, int(pct / 5))
            bar = "█" * bar_len
            click.echo(f"    {a['agent_name']:<16} {bar} {a['count']}次 ({pct:.1f}%)")
        click.echo("")

    # 周报摘要
    weekly = analyzer.weekly_report(7)
    click.echo(f"  📈 近7天统计:")
    click.echo(f"    会话: {weekly['total_sessions']} 次")
    click.echo(f"    成本: ${weekly['total_cost']:.4f}")
    click.echo(f"    Token: {format_tokens(weekly['total_tokens'])}")
    click.echo(f"{'='*50}\n")


# ============ 报告命令 ============

@cli.command()
@click.option("--output", "-o", default=None, help="输出路径")
@click.option("--open", "open_browser", is_flag=True, help="自动打开浏览器")
@click.pass_context
def report(ctx, output, open_browser):
    """📈 生成HTML分析报告"""
    reporter = ctx.obj["reporter"]
    path = reporter.generate_report(output_path=output)

    click.echo(f"\n  ✅ HTML报告已生成!")
    click.echo(f"  📄 路径: {path}\n")

    if open_browser:
        reporter.open_report(path)
        click.echo("  🌐 已在浏览器中打开报告\n")


# ============ 导出命令 ============

@cli.command()
@click.argument("session_id")
@click.option("--format", "-f", "fmt", type=click.Choice(["json", "markdown"]), default="json")
@click.pass_context
def export(ctx, session_id, fmt):
    """💾 导出会话记录"""
    storage = ctx.obj["storage"]
    path = storage.export_session(session_id, fmt)

    if path:
        click.echo(f"\n  ✅ 已导出为 {fmt.upper()} 格式")
        click.echo(f"  📄 路径: {path}\n")
    else:
        click.echo(f"\n  ❌ 导出失败: 未找到会话 {session_id}\n")


# ============ 删除命令 ============

@cli.command()
@click.argument("session_id")
@click.confirmation_option(prompt="确定要删除此会话吗?")
@click.pass_context
def delete(ctx, session_id):
    """🗑️ 删除会话记录"""
    storage = ctx.obj["storage"]
    if storage.delete_session(session_id):
        click.echo(f"\n  ✅ 已删除会话: {session_id}\n")
    else:
        click.echo(f"\n  ❌ 未找到会话: {session_id}\n")


# ============ 清理命令 ============

@cli.command()
@click.option("--days", "-d", default=90, help="清理N天前的会话")
@click.confirmation_option(prompt="确定要清理旧会话吗?")
@click.pass_context
def clean(ctx, days):
    """🧹 清理旧会话记录"""
    click.echo(f"\n  🧹 清理 {days} 天前的会话...\n")
    click.echo("  功能开发中，敬请期待!\n")


# ============ 交互式模式 ============

@cli.command()
@click.pass_context
def dashboard(ctx):
    """🖥️ 启动交互式仪表盘"""
    click.echo(f"""
{'='*50}
  🖥️  AgentScribe 交互式仪表盘 (v{__version__})
{'='*50}
  可用命令:
    list        - 列出最近会话
    stats       - 查看全局统计
    report      - 生成HTML报告
    view <id>   - 查看会话详情
    record      - 录制新会话
    export <id> - 导出会话
    help        - 显示帮助
    quit        - 退出
{'='*50}
""")
    while True:
        try:
            cmd = click.prompt("\n  agentscribe", default="")
            if cmd in ("quit", "q", "exit"):
                click.echo("  👋 再见!")
                break
            elif cmd == "list":
                ctx.invoke(list)
            elif cmd == "stats":
                ctx.invoke(stats)
            elif cmd == "report":
                ctx.invoke(report)
            elif cmd.startswith("view "):
                ctx.invoke(view, session_id=cmd[5:].strip())
            elif cmd == "record":
                ctx.invoke(record)
            elif cmd.startswith("export "):
                parts = cmd[7:].strip().split()
                sid = parts[0] if parts else ""
                fmt = parts[1] if len(parts) > 1 else "json"
                ctx.invoke(export, session_id=sid, fmt=fmt)
            elif cmd in ("help", "h", "?"):
                click.echo("""
  可用命令:
    list              - 列出最近会话
    stats             - 查看全局统计
    report            - 生成HTML报告
    view <session_id> - 查看会话详情
    record            - 录制新会话
    export <id>       - 导出会话
    help              - 显示帮助
    quit              - 退出
                """)
            else:
                click.echo(f"  ❌ 未知命令: {cmd}，输入 'help' 查看帮助")
        except (KeyboardInterrupt, EOFError):
            click.echo("\n  👋 再见!")
            break


@cli.command()
def version():
    """显示版本信息"""
    click.echo(f"AgentScribe v{__version__}")


if __name__ == "__main__":
    cli()