"""统计计算模块 - 对数值型数据列计算描述性统计量。

提供 compute_stats() 函数，对数据集的数值列计算：
均值、标准差、最小值、25%分位数、中位数、75%分位数、最大值。
"""

from __future__ import annotations
import math
from typing import Any


def _percentile(sorted_values: list[float], p: float) -> float:
    """计算百分位数（线性插值法）。

    Args:
        sorted_values: 已排序的数值列表
        p: 百分位（0-100）
    """
    if not sorted_values:
        return 0.0
    n = len(sorted_values)
    k = (p / 100) * (n - 1)
    f = int(k)
    c = k - f
    if f + 1 < n:
        return sorted_values[f] + c * (sorted_values[f + 1] - sorted_values[f])
    return sorted_values[f]


def compute_stats(data: dict[str, Any]) -> dict[str, dict[str, float]]:
    """计算数据集中所有数值列的描述性统计。

    Args:
        data: loader.load_csv() 返回的数据字典

    Returns:
        {列名: {统计量名: 值}}，每个列包含:
            mean, std, min, q25, median, q75, max, count
    """
    headers = data["headers"]
    rows = data["rows"]
    numeric_cols = data["numeric_cols"]

    if not numeric_cols:
        return {}

    # 提取各数值列的数据
    col_data: dict[str, list[float]] = {col: [] for col in numeric_cols}
    for row in rows:
        for col in numeric_cols:
            idx = headers.index(col)
            if idx < len(row) and isinstance(row[idx], (int, float)):
                col_data[col].append(row[idx])

    # 计算统计量
    result: dict[str, dict[str, float]] = {}
    for col, values in col_data.items():
        if not values:
            continue
        n = len(values)
        sorted_vals = sorted(values)
        mean_val = sum(values) / n
        variance = sum((x - mean_val) ** 2 for x in values) / n
        std_val = math.sqrt(variance)

        result[col] = {
            "count": n,
            "mean": round(mean_val, 4),
            "std": round(std_val, 4),
            "min": round(sorted_vals[0], 4),
            "q25": round(_percentile(sorted_vals, 25), 4),
            "median": round(_percentile(sorted_vals, 50), 4),
            "q75": round(_percentile(sorted_vals, 75), 4),
            "max": round(sorted_vals[-1], 4),
        }

    return result
