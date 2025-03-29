import torch

print(f"PyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")
print(f"GPU型号: {torch.cuda.get_device_name(0)}")
print(f"CUDA工具包版本: {torch.version.cuda}")
print(f"cuDNN版本: {torch.backends.cudnn.version()}")