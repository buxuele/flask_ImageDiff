import os
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from tqdm import tqdm
from pathlib import Path
import logging
from typing import List, Tuple, Dict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_thumbnails(input_dir: Path, output_dir: Path, target_size: Tuple[int, int] = (256, 256)) -> None:
    """创建缩略图并保存元数据"""
    logger.info("开始创建缩略图...")
    
    # 准备存储元数据的列表
    metadata = []

    # 如果 output_dir 有东西，先清空
    if output_dir.exists():
        for f in output_dir.iterdir():
            #  Remove this file or link.  If the path is a directory, use rmdir() instead.
            f.unlink()


    # 获取所有图片文件
    image_files = list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.png"))
    
    for img_path in tqdm(image_files, desc="处理图片"):
        try:
            # 读取原始图片
            img = Image.open(img_path)
            
            # 保存原始尺寸
            original_size = img.size
            
            # 创建缩略图
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # 保存缩略图
            thumbnail_path = output_dir / f"thumb_{img_path.name}"
            img.save(thumbnail_path, quality=95)
            
            # 记录元数据
            metadata.append({
                'original_path': str(img_path.name),
                'thumbnail_path': str(thumbnail_path.name),
                'original_size': f"{original_size[0]}x{original_size[1]}",
                'thumbnail_size': f"{img.size[0]}x{img.size[1]}"
            })
            
        except Exception as e:
            logger.error(f"处理图片 {img_path} 时出错: {str(e)}")
    
    # 保存元数据到CSV
    df = pd.DataFrame(metadata)
    df.to_csv("image_metadata.csv", index=False)
    logger.info(f"缩略图创建完成，共处理 {len(metadata)} 张图片")

def load_metadata() -> pd.DataFrame:
    """加载图片元数据"""
    return pd.read_csv("image_metadata.csv") 