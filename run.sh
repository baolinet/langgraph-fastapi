#!/bin/bash
# FastAPI 项目启动脚本

echo "============================================================"
echo "🚀 启动 FastAPI 项目"
echo "============================================================"

# 配置
HOST="127.0.0.1"
PORT="8000"
RELOAD="--reload"
DB_FILE="agents.db"
PYTHON_BIN=""
USE_UV="false"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 环境
echo ""
echo "📦 检查 Python 环境..."
if command -v uv &> /dev/null; then
    USE_UV="true"
    echo "✅ 使用 uv 运行环境"
elif command -v python3.12 &> /dev/null; then
    PYTHON_BIN="python3.12"
    echo "✅ 使用 Python 3.12 运行环境"
elif command -v python3 &> /dev/null; then
    PYTHON_BIN="python3"
    echo "✅ 使用 Python 运行环境"
elif command -v python &> /dev/null; then
    PYTHON_BIN="python"
    echo "✅ 使用 Python 运行环境"
else
    echo -e "${RED}❌ 未找到 Python 或 uv${NC}"
    exit 1
fi

# 检查端口是否被占用
echo ""
echo "🔍 检查端口 ${PORT}..."
if lsof -Pi :${PORT} -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  端口 ${PORT} 已被占用${NC}"
    echo "   正在停止占用端口的进程..."
    
    # 杀死占用端口的进程
    lsof -ti:${PORT} | xargs kill -9 2>/dev/null
    sleep 2
    
    # 再次检查
    if lsof -Pi :${PORT} -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}❌ 无法释放端口 ${PORT}${NC}"
        exit 1
    else
        echo "✅ 端口已释放"
    fi
else
    echo "✅ 端口 ${PORT} 可用"
fi

# 检查数据库文件
echo ""
echo "🗄️  检查数据库..."
if [ ! -f "${DB_FILE}" ]; then
    echo "⚠️  数据库文件不存在，正在初始化..."
    if [ "${USE_UV}" = "true" ]; then
        uv run tests/init_db.py
    else
        "${PYTHON_BIN}" tests/init_db.py
    fi
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 数据库初始化失败${NC}"
        exit 1
    fi
else
    echo "✅ 数据库文件存在"
fi

# 启动服务器
echo ""
echo "🌐 启动服务器..."
echo "   地址：http://${HOST}:${PORT}"
echo "   文档：http://${HOST}:${PORT}/docs"
echo "   重启：${RELOAD}"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "============================================================"
echo ""

# 使用 exec 替换当前进程，这样可以正确接收 Ctrl+C 信号
if [ "${USE_UV}" = "true" ]; then
    exec uv run uvicorn main:app --host "${HOST}" --port "${PORT}" ${RELOAD}
else
    exec "${PYTHON_BIN}" -m uvicorn main:app --host "${HOST}" --port "${PORT}" ${RELOAD}
fi
