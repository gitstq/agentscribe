#!/bin/bash
"""
AgentScribe 一键安装脚本
支持: Linux (deb/rpm), macOS, Windows (Git Bash)
"""

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}"
echo "  ╔═══════════════════════════════════════════╗"
echo "  ║        AgentScribe 安装脚本              ║"
echo "  ║  AI编码代理会话记录与智能分析工具         ║"
echo "  ╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# 检查Python版本
echo -e "${BLUE}🔍${NC} 检查Python版本..."
PYTHON=""
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        VER=$($cmd --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
        MAJOR=$(echo $VER | cut -d. -f1)
        MINOR=$(echo $VER | cut -d. -f2)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON=$cmd
            echo -e "${GREEN}✅${NC} 发现 Python $VER"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ 需要 Python 3.10+，请先安装"
    exit 1
fi

# 安装依赖
echo -e "${BLUE}📦${NC} 安装依赖..."
$PYTHON -m pip install --upgrade pip --break-system-packages 2>/dev/null || true
$PYTHON -m pip install -r requirements.txt --break-system-packages

# 安装AgentScribe
echo -e "${BLUE}📦${NC} 安装AgentScribe..."
$PYTHON -m pip install -e . --break-system-packages

# 验证安装
echo -e "${BLUE}🔍${NC} 验证安装..."
if $PYTHON -m agentscribe --help &> /dev/null; then
    echo -e "${GREEN}✅${NC} 安装成功!"
    echo ""
    echo -e "  运行 ${GREEN}agentscribe --help${NC} 查看帮助"
    echo -e "  运行 ${GREEN}agentscribe dashboard${NC} 启动交互式仪表盘"
    echo -e "  运行 ${GREEN}agentscribe record${NC} 录制新会话"
else
    echo "❌ 安装验证失败"
    exit 1
fi