# import torch
# from torchvision import models, transforms
# from PIL import Image
# from typing import Dict
# import numpy as np
# import logging
#
# logger = logging.getLogger(__name__)
#
# class DeepProcessor:
#     def __init__(self):
#         # 强制使用GPU，如果没有GPU则报错
#         if not torch.cuda.is_available():
#             raise RuntimeError("需要GPU支持，但未检测到可用的GPU")
#
#         self.device = torch.device('cuda')
#         self.model = None
#         self.transform = transforms.Compose([
#             transforms.Resize((224, 224)),
#             transforms.ToTensor(),
#             transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
#         ])
#
#         # 预加载模型到GPU
#         self._init_model()
#
#     def _init_model(self):
#         """初始化深度学习模型"""
#         if self.model is None:
#             logger.info("正在加载深度学习模型到GPU...")
#             self.model = models.resnet50(pretrained=True)
#             self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
#             self.model = self.model.to(self.device)
#             self.model.eval()
#             # 使用torch.cuda.amp进行混合精度训练
#             self.scaler = torch.cuda.amp.GradScaler()
#             logger.info("模型加载完成")
#
#     def extract_features(self, image_path: str) -> Dict:
#         """提取深度学习特征"""
#         try:
#             # 加载和预处理图片
#             img = Image.open(image_path).convert('RGB')
#             img_tensor = self.transform(img).unsqueeze(0).to(self.device)
#
#             # 使用混合精度计算
#             with torch.cuda.amp.autocast():
#                 with torch.no_grad():
#                     features = self.model(img_tensor)
#                     features = features.squeeze().cpu().numpy()
#
#             return {
#                 'deep_features': features
#             }
#         except Exception as e:
#             logger.error(f"提取深度学习特征时出错 {image_path}: {str(e)}")
#             return None
#
#     def calculate_similarity(self, feat1: Dict, feat2: Dict) -> float:
#         """计算两张图片的深度学习特征相似度"""
#         if feat1 is None or feat2 is None:
#             return 0.0
#
#         # 将特征转移到GPU进行计算
#         feat1_tensor = torch.from_numpy(feat1['deep_features']).to(self.device)
#         feat2_tensor = torch.from_numpy(feat2['deep_features']).to(self.device)
#
#         # 使用GPU计算余弦相似度
#         feat1_norm = feat1_tensor / torch.norm(feat1_tensor)
#         feat2_norm = feat2_tensor / torch.norm(feat2_tensor)
#         similarity = torch.dot(feat1_norm, feat2_norm).cpu().item()
#
#         return float(similarity)