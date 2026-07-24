"""数据加载模块 - 负责读取和预处理CSV数据文件。

提供 load_csv() 函数，自动检测编码、识别列类型、处理缺失值。
"""

from __future__ import annotations
import csv
from pathlib import Path
from typing import Any

# 尝试的编码顺序
_ENCODINGS = ["utf-8", "gbk", "gb2312", "latin-1"]


def load_csv(filepath: str) -> dict[str, Any]:
    """加载CSV文件，返回包含数据和元信息的字典。

    自动尝试多种编码：UTF-8 → GBK → GB2312 → Latin-1。

    Args:
        filepath: CSV文件路径

    Returns:
        dict with keys:
            - headers: list[str] 列名
            - rows: list[list[str|float]] 数据行
            - numeric_cols: list[str] 数值型列名
            - missing_count: dict[str, int] 各列缺失值数量

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件为空或格式不正确
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {filepath}")

    rows = None
    last_error = None
    for encoding in _ENCODINGS:
        try:
            with open(filepath, "r", encoding=encoding) as f:
                reader = csv.reader(f)
                rows = list(reader)
            break
        except UnicodeDecodeError as e:
            last_error = e
            continue

    if rows is None:
        raise ValueError(
            f"无法解析文件编码，已尝试: {', '.join(_ENCODINGS)}。\n"
            f"最后错误: {last_error}"
        )

    if not rows:
        raise ValueError("文件为空")

    headers = [h.strip() for h in rows[0]]
    data = rows[1:]

    if not data:
        raise ValueError("文件只有表头，没有数据行")

    # 检测每列的数值类型
    numeric_cols = []
    parsed_data = []

    for row in data:
        parsed_row = []
        for i, value in enumerate(row):
            if i >= len(headers):
                continue
            v = value.strip()
            if v == "":
                parsed_row.append(None)
            else:
                try:
                    parsed_row.append(float(v))
                except ValueError:
                    parsed_row.append(v)
        if len(parsed_row) == len(headers):
            parsed_data.append(parsed_row)

    # 判断哪些列是数值型
    for col_idx, col_name in enumerate(headers):
        num_count = 0
        for row in parsed_data:
            if col_idx < len(row) and isinstance(row[col_idx], (int, float)):
                num_count += 1
        if num_count > len(parsed_data) * 0.5:
            numeric_cols.append(col_name)

    # 缺失值统计
    missing_count = {}
    for col_idx, col_name in enumerate(headers):
        missing = sum(1 for row in parsed_data
                      if col_idx >= len(row) or row[col_idx] is None)
        if missing > 0:
            missing_count[col_name] = missing

    return {
        "headers": headers,
        "rows": parsed_data,
        "numeric_cols": numeric_cols,
        "missing_count": missing_count,
    }
