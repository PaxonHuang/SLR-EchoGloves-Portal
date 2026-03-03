#!/bin/bash
# 手势识别可视化系统启动脚本

echo "手势识别可视化系统启动器"
echo "=========================="

# 检查Python3.11是否可用
if command -v /usr/local/bin/python3.11 &> /dev/null
then
    echo "使用 Python 3.11"
    PYTHON_CMD="/usr/local/bin/python3.11"
elif command -v python3 &> /dev/null
then
    echo "使用 python3"
    PYTHON_CMD="python3"
else
    echo "错误: 未找到Python3"
    exit 1
fi

# 进入项目目录
cd "$(dirname "$0")"

echo "正在启动应用程序..."
echo ""

# 启动应用程序
$PYTHON_CMD start.py