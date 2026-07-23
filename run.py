"""datasense 启动脚本 - 用于未安装或无法找到命令时的直接运行。

用法:
    python run.py stats examples/iris.csv
    python run.py summary examples/iris.csv
    python run.py plot examples/iris.csv --x sepal_length --y sepal_width
"""

import sys
import os

# 确保能找到 datasense 包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datasense.cli import main

main()
