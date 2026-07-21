"""测试数据加载模块。"""

import pytest
import tempfile
import os
from datasense.loader import load_csv


@pytest.fixture
def sample_csv():
    """创建测试用的临时CSV文件。"""
    content = "name,age,score,city\nAlice,20,85.5,Beijing\nBob,21,92.0,Shanghai\nCharlie,,78.5,Guangzhou\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        f.write(content)
        path = f.name
    yield path
    os.unlink(path)


def test_load_basic(sample_csv):
    """测试基本加载功能。"""
    data = load_csv(sample_csv)
    assert len(data["headers"]) == 4
    assert data["headers"] == ["name", "age", "score", "city"]
    assert len(data["rows"]) == 3


def test_numeric_detection(sample_csv):
    """测试数值列自动识别。"""
    data = load_csv(sample_csv)
    assert "age" in data["numeric_cols"]
    assert "score" in data["numeric_cols"]
    assert "name" not in data["numeric_cols"]


def test_missing_values(sample_csv):
    """测试缺失值统计。"""
    data = load_csv(sample_csv)
    assert "age" in data["missing_count"]
    assert data["missing_count"]["age"] == 1


def test_file_not_found():
    """测试文件不存在的情况。"""
    with pytest.raises(FileNotFoundError):
        load_csv("/nonexistent/file.csv")


def test_empty_csv():
    """测试空文件。"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        path = f.name
    try:
        with pytest.raises(ValueError):
            load_csv(path)
    finally:
        os.unlink(path)


def test_gbk_encoding():
    """测试GBK编码的中文CSV文件能正常加载。"""
    content = "姓名,年龄,成绩\n张三,20,85.5\n李四,21,92.0\n"
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as f:
        f.write(content.encode("gbk"))
        path = f.name
    try:
        data = load_csv(path)
        assert data["headers"] == ["姓名", "年龄", "成绩"]
        assert len(data["rows"]) == 2
        assert data["rows"][0][0] == "张三"
    finally:
        os.unlink(path)


def test_all_encodings_fail():
    """测试所有编码都失败时抛出 ValueError。"""
    # 创建一个全是二进制数据的"CSV"文件
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as f:
        f.write(b"\xff\xfe\x00\x01\x02\x03")
        path = f.name
    try:
        with pytest.raises(ValueError, match="无法解析文件编码"):
            load_csv(path)
    finally:
        os.unlink(path)
