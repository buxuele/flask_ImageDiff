import sys
import torch

# 检查  GPU 是否可用
ret = torch.cuda.is_available()
print(ret)
print(torch.cuda.current_device())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(0))

print()
print("Python version: ", sys.version)
print("torch version: ", torch.__version__)
print("cudu version: ", torch.version.cuda)


"""输出:
# 其他办法都失败，就是使用这个！ 安装成功。

# 这个默认下载最新的。
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118 

# 指定torch 的版本！
pip3 install torch==2.0.1 torchvision --index-url https://download.pytorch.org/whl/cu118 

NVIDIA GeForce RTX 3060
Python version:  3.10.12
torch version:  2.0.1+cu118
cudu version:  11.8
"""
