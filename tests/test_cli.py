import subprocess
import sys
import os
import pytest
import tempfile


def run_cli(*args):
    result = subprocess.run(
        [sys.executable, "-m", "datasense.cli"] + list(args),
        capture_output=True, text=True,
        cwd=os.path.join(os.path.dirname(__file__), "..")
    )
    return result


def test_summary():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "examples", "iris.csv")
    result = run_cli("summary", csv_path)
    assert result.returncode == 0
    assert "sepal_length" in result.stdout
    assert "行数: 15" in result.stdout


def test_stats():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "examples", "iris.csv")
    result = run_cli("stats", csv_path)
    assert result.returncode == 0
    assert "mean=" in result.stdout


def test_plot():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "examples", "iris.csv")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        outpath = f.name
    try:
        result = run_cli("plot", csv_path, "--x", "sepal_length", "--y", "sepal_width", "-o", outpath)
        assert result.returncode == 0
        assert os.path.exists(outpath)
    finally:
        os.unlink(outpath)


def test_no_args():
    result = run_cli()
    assert result.returncode == 1


def test_file_not_found():
    result = run_cli("summary", "/nonexistent.csv")
    assert result.returncode == 1
