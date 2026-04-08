#!/bin/bash
# 运行所有测试的快捷脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "🧪 运行所有测试"
echo "============================================================"

# 检查 Python 环境
echo ""
echo "📦 检查 Python 环境..."
if command -v uv &> /dev/null; then
    PYTHON_CMD="uv run python"
    echo "✅ 使用 uv 运行环境"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✅ 使用 Python 运行环境"
else
    echo -e "${RED}❌ 未找到 Python 或 uv${NC}"
    exit 1
fi

# 检查服务器是否运行
echo ""
echo "📡 检查服务器状态..."
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "✅ 服务器正在运行"
else
    echo -e "${YELLOW}⚠️  服务器未运行${NC}"
    echo ""
    echo "请先启动服务器："
    echo "   ./run.sh"
    echo ""
    echo "或者现在自动启动？(y/n)"
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🚀 启动服务器..."
        ./run.sh &
        sleep 5
    else
        exit 1
    fi
fi

# 初始化测试数据（如果需要）
echo ""
echo "📝 初始化测试数据..."
$PYTHON_CMD tests/init_db.py

# 运行测试
echo ""
echo "🧪 运行测试..."
echo ""

TEST_FAILED=0

echo "============================================================"
echo "📋 测试 1: 双认证机制测试"
echo "============================================================"
$PYTHON_CMD tests/test_auth.py
if [ $? -ne 0 ]; then
    TEST_FAILED=1
fi

echo ""
echo "============================================================"
echo "📋 测试 2: 统一响应格式测试"
echo "============================================================"
$PYTHON_CMD tests/test_response_format.py
if [ $? -ne 0 ]; then
    TEST_FAILED=1
fi

echo ""
echo "============================================================"
echo "📋 测试 3: 用户管理接口完整测试"
echo "============================================================"
$PYTHON_CMD tests/test_users.py
if [ $? -ne 0 ]; then
    TEST_FAILED=1
fi

echo ""
echo "============================================================"
echo "📋 测试 4: Agent 接口测试"
echo "============================================================"
$PYTHON_CMD tests/test_agents.py
if [ $? -ne 0 ]; then
    TEST_FAILED=1
fi

echo ""
echo "============================================================"
echo "📊 测试总结"
echo "============================================================"
if [ $TEST_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}❌ 部分测试失败${NC}"
    exit 1
fi
