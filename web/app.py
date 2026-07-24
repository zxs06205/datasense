"""DataSense Web应用 - 本地网页端数据分析工具"""

import os
import sys
import tempfile
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 添加父目录到路径，以便导入datasense模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制

# 存储当前加载的数据
current_data = {}
current_filename = {}


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """上传CSV文件"""
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'error': '请上传CSV文件'}), 400

    try:
        # 尝试多种编码读取CSV文件（与CLI loader同样逻辑）
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        df = None
        last_error = None
        for enc in encodings:
            try:
                file.stream.seek(0)
                df = pd.read_csv(file.stream, encoding=enc)
                break
            except (UnicodeDecodeError, UnicodeError) as e:
                last_error = e
                continue

        if df is None:
            return jsonify({'error': f'无法解析文件编码，请确认文件为CSV格式。最后错误: {str(last_error)}'}), 400

        session_id = 'default'
        current_data[session_id] = df
        current_filename[session_id] = file.filename

        return jsonify({
            'success': True,
            'filename': file.filename,
            'rows': len(df),
            'columns': list(df.columns)
        })
    except Exception as e:
        return jsonify({'error': f'读取文件失败: {str(e)}'}), 500


@app.route('/load-sample', methods=['POST'])
def load_sample():
    """加载示例数据集"""
    try:
        # 获取当前web应用所在目录
        web_dir = os.path.dirname(os.path.abspath(__file__))
        # datasense项目根目录（web目录的父目录）
        project_dir = os.path.dirname(web_dir)
        # 示例数据路径
        sample_path = os.path.join(project_dir, 'examples', 'iris.csv')

        print(f"Loading sample from: {sample_path}")  # 调试用

        if not os.path.exists(sample_path):
            return jsonify({'error': f'示例文件不存在: {sample_path}'}), 404

        df = pd.read_csv(sample_path)
        session_id = 'default'
        current_data[session_id] = df
        current_filename[session_id] = 'iris.csv'

        return jsonify({
            'success': True,
            'filename': 'iris.csv (示例数据)',
            'rows': len(df),
            'columns': list(df.columns)
        })
    except Exception as e:
        return jsonify({'error': f'加载示例数据失败: {str(e)}'}), 500


@app.route('/summary')
def get_summary():
    """获取数据概览"""
    session_id = 'default'
    if session_id not in current_data:
        return jsonify({'error': '请先上传或加载数据'}), 400

    df = current_data[session_id]

    # 构建摘要信息
    summary = {
        'filename': current_filename.get(session_id, '未知'),
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': []
    }

    for col in df.columns:
        col_info = {
            'name': col,
            'dtype': str(df[col].dtype),
            'non_null': int(df[col].count()),
            'null': int(df[col].isnull().sum()),
            'null_percent': round(df[col].isnull().sum() / len(df) * 100, 2)
        }
        summary['columns'].append(col_info)

    return jsonify(summary)


@app.route('/stats')
def get_stats():
    """获取统计信息"""
    session_id = 'default'
    if session_id not in current_data:
        return jsonify({'error': '请先上传或加载数据'}), 400

    df = current_data[session_id]

    # 只统计数值列
    numeric_df = df.select_dtypes(include=['int64', 'float64'])

    if numeric_df.empty:
        return jsonify({'error': '没有数值型列可供统计'}), 400

    stats = {}
    for col in numeric_df.columns:
        stats[col] = {
            'mean': round(float(numeric_df[col].mean()), 4),
            'std': round(float(numeric_df[col].std()), 4),
            'min': round(float(numeric_df[col].min()), 4),
            '25%': round(float(numeric_df[col].quantile(0.25)), 4),
            '50%': round(float(numeric_df[col].quantile(0.5)), 4),
            '75%': round(float(numeric_df[col].quantile(0.75)), 4),
            'max': round(float(numeric_df[col].max()), 4)
        }

    return jsonify(stats)


@app.route('/plot', methods=['POST'])
def create_plot():
    """生成图表"""
    session_id = 'default'
    if session_id not in current_data:
        return jsonify({'error': '请先上传或加载数据'}), 400

    df = current_data[session_id]
    data = request.get_json()

    x_col = data.get('x_column')
    y_col = data.get('y_column')
    plot_type = data.get('plot_type', 'scatter')

    if not x_col or not y_col:
        return jsonify({'error': '请选择X轴和Y轴的列'}), 400

    if x_col not in df.columns or y_col not in df.columns:
        return jsonify({'error': '选择的列不存在'}), 400

    try:
        plt.figure(figsize=(10, 6))

        if plot_type == 'scatter':
            plt.scatter(df[x_col], df[y_col], alpha=0.6, c='steelblue', edgecolors='white', s=50)
            plt.xlabel(x_col, fontsize=12)
            plt.ylabel(y_col, fontsize=12)
            plt.title(f'{y_col} vs {x_col}', fontsize=14)
            plt.grid(True, alpha=0.3)

        elif plot_type == 'histogram':
            plt.hist(df[x_col], bins=20, color='steelblue', edgecolor='white', alpha=0.7)
            plt.xlabel(x_col, fontsize=12)
            plt.ylabel('Frequency', fontsize=12)
            plt.title(f'{x_col} Distribution', fontsize=14)
            plt.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        # 保存图片
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'plot.png')
        plt.savefig(img_path, dpi=150, bbox_inches='tight')
        plt.close()

        return send_file(img_path, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': f'生成图表失败: {str(e)}'}), 500


@app.route('/preview')
def preview_data():
    """预览数据（前10行）"""
    session_id = 'default'
    if session_id not in current_data:
        return jsonify({'error': '请先上传或加载数据'}), 400

    df = current_data[session_id]
    preview = df.head(10).to_dict(orient='records')
    return jsonify({
        'columns': list(df.columns),
        'data': preview
    })


def open_browser():
    """延迟打开浏览器"""
    webbrowser.open('http://localhost:5000')


if __name__ == '__main__':
    print("=" * 50)
    print("  DataSense Web Server")
    print("  Opening browser automatically...")
    print("  URL: http://localhost:5000")
    print("=" * 50)

    # 延迟1.5秒后自动打开浏览器
    threading.Timer(1.5, open_browser).start()

    app.run(debug=False, host='127.0.0.1', port=5000)
