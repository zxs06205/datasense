"""测试可视化模块。"""

import pytest
import tempfile
import os
from datasense.visualize import plot_scatter, plot_histogram


def make_data(x_name, y_name, x_vals, y_vals):
    """构造测试数据。"""
    return {
        "headers": [x_name, y_name],
        "rows": [[x, y] for x, y in zip(x_vals, y_vals)],
        "numeric_cols": [x_name, y_name],
        "missing_count": {},
    }


def test_plot_scatter():
    """测试散点图生成。"""
    data = make_data("x", "y",
                     [1.0, 2.0, 3.0, 4.0, 5.0],
                     [2.0, 4.0, 6.0, 8.0, 10.0])
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        result = plot_scatter(data, "x", "y", output=path)
        assert result == path
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_plot_histogram():
    """测试直方图生成。"""
    data = make_data("val", "dummy",
                     [1.0, 2.0, 2.0, 3.0, 3.0, 3.0],
                     [0, 0, 0, 0, 0, 0])
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        result = plot_histogram(data, "val", output=path)
        assert result == path
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_invalid_column():
    """测试不存在的列。"""
    data = make_data("x", "y", [1.0], [2.0])
    with pytest.raises(ValueError, match="不存在"):
        plot_scatter(data, "z", "y")


def test_non_numeric_column():
    """测试非数值列。"""
    data = {
        "headers": ["name", "age"],
        "rows": [["Alice", 20]],
        "numeric_cols": ["age"],
        "missing_count": {},
    }
    with pytest.raises(ValueError, match="不是数值列"):
        plot_scatter(data, "name", "age")
