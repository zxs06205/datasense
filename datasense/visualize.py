"""可视化模块 - 使用matplotlib生成散点图和直方图。

提供 plot_scatter() 和 plot_histogram() 函数。
"""

import matplotlib
matplotlib.use("Agg")  # 非交互后端

import matplotlib.pyplot as plt
from pathlib import Path
from typing import Any


def _setup_chinese_font():
    """配置中文字体支持。"""
    found = False
    try:
        import matplotlib.font_manager as fm
        import warnings
        # 尝试常见中文字体
        for font_name in ["SimHei", "WenQuanYi Micro Hei", "Noto Sans CJK SC",
                          "Source Han Sans SC", "DejaVu Sans"]:
            try:
                fm.findfont(font_name, fallback_to_default=False)
                plt.rcParams["font.sans-serif"] = [font_name]
                found = True
                break
            except Exception:
                continue
    except Exception:
        pass

    if not found:
        import warnings
        warnings.warn(
            "未找到中文字体，图表中的中文可能无法正常显示。"
            "请安装中文字体包（如 fonts-wqy-microhei）"
        )

    plt.rcParams["axes.unicode_minus"] = False


def _get_numeric_values(data: dict[str, Any], col_name: str) -> list[float]:
    """从数据中提取指定列的数值。"""
    headers = data["headers"]
    if col_name not in headers:
        raise ValueError(f"列 '{col_name}' 不存在")
    idx = headers.index(col_name)
    values = []
    for row in data["rows"]:
        if idx < len(row) and isinstance(row[idx], (int, float)):
            values.append(row[idx])
    return values


def plot_scatter(data: dict[str, Any], x_col: str, y_col: str,
                 output: str = "scatter.png") -> str:
    """生成散点图。

    Args:
        data: loader.load_csv() 返回的数据字典
        x_col: x轴列名
        y_col: y轴列名
        output: 输出文件路径

    Returns:
        输出文件路径
    """
    x_vals = _get_numeric_values(data, x_col)
    y_vals = _get_numeric_values(data, y_col)

    if not x_vals or not y_vals:
        raise ValueError(f"列 '{x_col}' 或 '{y_col}' 不是数值列或数据为空")

    # 取两个列的最小长度
    min_len = min(len(x_vals), len(y_vals))
    x_vals = x_vals[:min_len]
    y_vals = y_vals[:min_len]

    _setup_chinese_font()
    plt.figure(figsize=(8, 6))
    plt.scatter(x_vals, y_vals, alpha=0.6, edgecolors="w", s=60)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(f"{x_col} vs {y_col}")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output, dpi=120)
    plt.close()
    return output


def plot_histogram(data: dict[str, Any], col_name: str,
                   output: str = "histogram.png") -> str:
    """生成直方图。

    Args:
        data: loader.load_csv() 返回的数据字典
        col_name: 要绘制直方图的列名
        output: 输出文件路径

    Returns:
        输出文件路径
    """
    values = _get_numeric_values(data, col_name)
    if not values:
        raise ValueError(f"列 '{col_name}' 不是数值列或数据为空")

    _setup_chinese_font()
    plt.figure(figsize=(8, 6))
    plt.hist(values, bins=20, edgecolor="white", alpha=0.7)
    plt.xlabel(col_name)
    plt.ylabel("Frequency")
    plt.title(f"Histogram of {col_name}")
    plt.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(output, dpi=120)
    plt.close()
    return output
