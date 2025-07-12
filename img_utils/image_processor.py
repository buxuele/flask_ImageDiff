import os
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from tqdm import tqdm
from pathlib import Path
import imagehash
from typing import List, Tuple, Dict
import logging

# import torch
# from torchvision import models, transforms
# from torch.nn import functional as F

from img_utils.make_small_images import create_thumbnails, load_metadata
from img_utils.hash_processor import HashProcessor
from img_utils.hist_processor import HistProcessor
# from img_utils.deep_processor import DeepProcessor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self, input_dir: str = "imgs", output_dir: str = "small_imgs"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化各个处理器
        self.hash_processor = HashProcessor()
        self.hist_processor = HistProcessor()
        # self.deep_processor = DeepProcessor()
    
    def create_thumbnails(self, target_size: tuple = (256, 256)) -> None:
        """创建缩略图并保存元数据"""
        create_thumbnails(self.input_dir, self.output_dir, target_size)
    
    def find_similar_images(self, similarity_threshold: float = 0.95, method: str = 'hash') -> List[Dict]:
        """查找相似图片
        
        Args:
            similarity_threshold: 相似度阈值
            method: 特征提取方法，可选 'hash'（哈希）, 'hist'（直方图）, 'deep'（深度学习）
        """
        logger.info(f"开始查找相似图片，使用 {method} 方法...")
        
        # 选择处理器
        processor = {
            'hash': self.hash_processor,
            'hist': self.hist_processor,
            # 'deep': self.deep_processor
        }.get(method)
        
        if processor is None:
            raise ValueError(f"不支持的方法: {method}")
        
        # 读取元数据
        df = load_metadata()
        similar_pairs = []
        
        # 为每张图片提取特征
        features = {}
        for _, row in tqdm(df.iterrows(), desc="提取特征", total=len(df)):
            features[row['original_path']] = processor.extract_features(
                str(self.output_dir / row['thumbnail_path'])
            )
        
        # 比较所有图片对
        for i, (img1_path, feat1) in enumerate(features.items()):
            if feat1 is None:
                continue
                
            for img2_path, feat2 in list(features.items())[i+1:]:
                if feat2 is None:
                    continue
                
                # 计算相似度
                similarity = processor.calculate_similarity(feat1, feat2)
                
                if similarity >= similarity_threshold:
                    similar_pairs.append({
                        'image1': img1_path,
                        'image2': img2_path,
                        'similarity': similarity
                    })
        
        logger.info(f"找到 {len(similar_pairs)} 对相似图片")
        return similar_pairs

if __name__ == "__main__":
    # 测试代码
    processor = ImageProcessor()
    processor.create_thumbnails()
    similar_pairs = processor.find_similar_images(method='hash')
    print(f"找到 {len(similar_pairs)} 对相似图片") 