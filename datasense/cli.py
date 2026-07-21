"""命令行接口模块 - 提供 datasense 命令的 CLI 入口。

子命令:
    summary <file>    数据概览
    stats <file>      描述性统计
    plot <file>       生成图表
"""

import argparse
import sys
from .loader import load_csv
from .stats import compute_stats
from .visualize import plot_scatter, plot_histogram


def cmd_summary(args: argparse.Namespace) -> None:
    """数据概览子命令。"""
    try:
        data = load_csv(args.file)
    except (FileNotFoundError, ValueError) as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"文件: {args.file}")
    print(f"行数: {len(data['rows'])}")
    print(f"列数: {len(data['headers'])}")
    print(f"列名: {', '.join(data['headers'])}")
    print(f"数值列: {', '.join(data['numeric_cols']) if data['numeric_cols'] else '无'}")
    if data["missing_count"]:
        print("缺失值:")
        for col, count in data["missing_count"].items():
            print(f"  {col}: {count}")


def cmd_stats(args: argparse.Namespace) -> None:
    """描述性统计子命令。"""
    try:
        data = load_csv(args.file)
    except (FileNotFoundError, ValueError) as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    stats = compute_stats(data)
    if not stats:
        print("没有可计算的数值列")
        return

    for col, s in stats.items():
        print(f"\n{col} (n={s['count']}):")
        print(f"  mean={s['mean']}, std={s['std']}")
        print(f"  min={s['min']}, q25={s['q25']}, median={s['median']}, q75={s['q75']}, max={s['max']}")


def cmd_plot(args: argparse.Namespace) -> None:
    """可视化子命令。"""
    try:
        data = load_csv(args.file)
    except (FileNotFoundError, ValueError) as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    if args.x and args.y:
        output = args.output or "scatter.png"
        path = plot_scatter(data, args.x, args.y, output)
    elif args.col:
        output = args.output or "histogram.png"
        path = plot_histogram(data, args.col, output)
    else:
        print("请指定 --x --y (散点图) 或 --col (直方图)", file=sys.stderr)
        sys.exit(1)

    print(f"图表已保存: {path}")


def main() -> None:
    """CLI主入口。"""
    parser = argparse.ArgumentParser(
        prog="datasense",
        description="CSV数据分析命令行工具",
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # summary
    p_summary = subparsers.add_parser("summary", help="显示数据概览")
    p_summary.add_argument("file", help="CSV文件路径")
    p_summary.set_defaults(func=cmd_summary)

    # stats
    p_stats = subparsers.add_parser("stats", help="计算描述性统计")
    p_stats.add_argument("file", help="CSV文件路径")
    p_stats.set_defaults(func=cmd_stats)

    # plot
    p_plot = subparsers.add_parser("plot", help="生成图表")
    p_plot.add_argument("file", help="CSV文件路径")
    p_plot.add_argument("--x", help="散点图X轴列名")
    p_plot.add_argument("--y", help="散点图Y轴列名")
    p_plot.add_argument("--col", help="直方图列名")
    p_plot.add_argument("-o", "--output", help="输出文件路径")
    p_plot.set_defaults(func=cmd_plot)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
