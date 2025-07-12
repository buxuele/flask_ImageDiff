from flask import Flask, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from img_utils.image_processor import ImageProcessor
import os
from pathlib import Path
import json
import shutil

app = Flask(__name__)

# 定义图片文件夹变量
image_input_folder = r" d:\Pictures\good ".strip()


# 配置静态文件目录
app.config['STATIC_FOLDER'] = 'static'

app.config['IMAGES_FOLDER'] = image_input_folder
app.secret_key = 'your-secret-key-here'  # 用于flash消息

#   def __init__(self, input_dir: str = "imgs", output_dir: str = "small_imgs"):
processor = ImageProcessor(input_dir=image_input_folder)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/file_count')
def file_count():
    """获取图片文件数量"""
    image_files = list(Path(image_input_folder).glob('*.jpg')) + list(Path(image_input_folder).glob('*.png'))
    return jsonify({'count': len(image_files)})

@app.route('/process', methods=['POST'])
def process_images():
    """处理图片并返回结果"""
    try:
        # 获取参数
        data = request.get_json()
        threshold = float(data.get('threshold', 98)) / 100  # 转换为0-1范围
        method = data.get('method', 'hash')  # 默认使用哈希方法

        # 验证方法
        if method not in ['hash', 'hist', 'deep']:
            raise ValueError(f"不支持的方法: {method}")

        # 创建缩略图
        processor.create_thumbnails()

        # 查找相似图片
        similar_pairs = processor.find_similar_images(
            similarity_threshold=threshold,
            method=method
        )

        # 将结果保存到JSON文件
        with open('similar_pairs.json', 'w', encoding='utf-8') as f:
            json.dump(similar_pairs, f, ensure_ascii=False, indent=2)

        return jsonify({
            'status': 'success',
            'message': f'找到 {len(similar_pairs)} 对相似图片'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/results')
def show_results():
    """显示相似图片结果"""
    # 读取相似图片对
    try:
        with open('similar_pairs.json', 'r', encoding='utf-8') as f:
            similar_pairs = json.load(f)
    except FileNotFoundError:
        similar_pairs = []

    # 将相似图片对分组
    groups = []
    used_images = set()

    for pair in similar_pairs:
        if pair['image1'] in used_images or pair['image2'] in used_images:
            continue

        group = [pair['image1'], pair['image2']]
        used_images.add(pair['image1'])
        used_images.add(pair['image2'])

        # 查找与当前组中图片相似的其他图片
        for other_pair in similar_pairs:
            if other_pair['image1'] in group and other_pair['image2'] not in used_images:
                group.append(other_pair['image2'])
                used_images.add(other_pair['image2'])
            elif other_pair['image2'] in group and other_pair['image1'] not in used_images:
                group.append(other_pair['image1'])
                used_images.add(other_pair['image1'])

        groups.append(group)  # 将分组添加到 groups 列表

    return render_template('results.html', groups=groups)


@app.route('/remove_duplicates', methods=['POST'])
def remove_duplicates():
    """移除重复图片"""
    try:
        # 创建重复图片目录
        dup_dir = Path('dup_imgs')
        dup_dir.mkdir(exist_ok=True)

        # 读取相似图片对
        with open('similar_pairs.json', 'r', encoding='utf-8') as f:
            similar_pairs = json.load(f)

        # 将相似图片对分组
        groups = []
        used_images = set()
        moved_count = 0

        for pair in similar_pairs:
            if pair['image1'] in used_images or pair['image2'] in used_images:
                continue

            group = [pair['image1'], pair['image2']]
            used_images.add(pair['image1'])
            used_images.add(pair['image2'])

            # 查找与当前组中图片相似的其他图片
            for other_pair in similar_pairs:
                if other_pair['image1'] in group and other_pair['image2'] not in used_images:
                    group.append(other_pair['image2'])
                    used_images.add(other_pair['image2'])
                elif other_pair['image2'] in group and other_pair['image1'] not in used_images:
                    group.append(other_pair['image1'])
                    used_images.add(other_pair['image1'])

            groups.append(group)  # 确保包含这行

            # 保留第一张图片，移动其他图片
            for img in group[1:]:
                src_path = Path(image_input_folder) / img
                dst_path = dup_dir / img
                if src_path.exists():
                    shutil.move(str(src_path), str(dst_path))
                    moved_count += 1

        flash(f'成功移动 {moved_count} 张重复图片到 dup_imgs 目录', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        flash(f'移除重复图片时出错: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/img/<path:filename>')
def serve_image(filename):
    """提供图片文件服务"""
    # 移除路径中的 imgs\ 前缀
    filename = filename.replace('imgs\\', '').replace('imgs/', '')
    return send_from_directory(image_input_folder, filename)


@app.route('/thumb/<path:filename>')
def serve_thumbnail(filename):
    """提供缩略图服务"""
    # 移除路径中的 small_imgs\ 前缀
    filename = filename.replace('small_imgs\\', '').replace('small_imgs/', '')
    return send_from_directory('small_imgs', filename)


if __name__ == '__main__':
    # 确保必要的目录存在
    Path(image_input_folder).mkdir(exist_ok=True)
    Path('small_imgs').mkdir(exist_ok=True)
    Path('templates').mkdir(exist_ok=True)
    Path('static').mkdir(exist_ok=True)

    # 创建错误图片
    error_img_path = Path('static/error.png')
    app.run(debug=True)


"""

操作步骤：

1. 修改顶部的文件夹路径。
2. 运行 app.py。

"""