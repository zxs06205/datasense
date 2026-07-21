"""测试统计计算模块。"""

from datasense.stats import compute_stats, _percentile


def make_data(numeric_cols, values_dict):
    """构造测试数据。"""
    headers = list(values_dict.keys())
    num_rows = max(len(v) for v in values_dict.values())
    rows = []
    for i in range(num_rows):
        row = []
        for h in headers:
            val = values_dict[h][i]
            row.append(val)
        rows.append(row)
    return {
        "headers": headers,
        "rows": rows,
        "numeric_cols": numeric_cols,
        "missing_count": {},
    }


def test_percentile():
    """测试百分位数计算。"""
    vals = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert _percentile(vals, 50) == 3.0
    assert _percentile(vals, 0) == 1.0
    assert _percentile(vals, 100) == 5.0


def test_compute_stats_basic():
    """测试基本统计计算。"""
    data = make_data(
        numeric_cols=["x"],
        values_dict={"x": [1.0, 2.0, 3.0, 4.0, 5.0]},
    )
    result = compute_stats(data)
    assert "x" in result
    assert result["x"]["count"] == 5
    assert result["x"]["mean"] == 3.0
    assert result["x"]["min"] == 1.0
    assert result["x"]["max"] == 5.0
    assert result["x"]["median"] == 3.0


def test_compute_stats_multiple_cols():
    """测试多列统计。"""
    data = make_data(
        numeric_cols=["a", "b"],
        values_dict={
            "a": [10.0, 20.0, 30.0],
            "b": [5.0, 15.0, 25.0],
        },
    )
    result = compute_stats(data)
    assert len(result) == 2
    assert result["a"]["mean"] == 20.0
    assert result["b"]["mean"] == 15.0


def test_no_numeric_cols():
    """测试无数值列的情况。"""
    data = make_data(
        numeric_cols=[],
        values_dict={"name": ["a", "b"]},
    )
    result = compute_stats(data)
    assert result == {}
