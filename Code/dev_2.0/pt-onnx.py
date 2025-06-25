from ultralytics import YOLO

# 加载预训练模型
model = YOLO("E:\\Code\\NJUST-AutoRobot\\GarbageClassification\\Code\\dev_2.0\\models\\small_base\\best-mix-yolov8s_ep100_batch16.pt")  # 替换为你的 .pt 文件路径

# 导出为 ONNX
model.export(
    format="onnx",
    imgsz=(640,640),        
    simplify=True,           # 简化模型结构
    opset=12,                # ONNX 算子版本
    dynamic=False,           # 禁用动态输入
)