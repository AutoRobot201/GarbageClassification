"""
YOLOv11 垃圾检测训练脚本适配test集版本
Created: 2024-04-01
"""
from ultralytics import YOLO
import torch
import os
from pathlib import Path

def main():
    # ================== 基础配置 ==================
    config = {
        # 数据集配置文件路径（建议使用绝对路径）
        'data_yaml': Path('E:/Code/NJUST-AutoRobot/GarbageClassification/Code/dev_2.0/garbage.yaml'),
        
        # 模型配置
        'pretrained_model': 'best-v20250330.pt',  # 预训练模型路径
        'output_dir': Path('Code/dev_2.0/runs/train'),  # 输出目录
        
        # 训练超参数
        'train_params': {
            'epochs': 100,
            'batch': 32,
            'imgsz': 640,
            'optimizer': 'AdamW',
            'lr0': 1e-3,
            'cos_lr': True,
            'patience': 30
        }
    }

    # ================== 路径预处理 ==================
    # 自动检测GPU设备
    config['device'] = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # 创建输出目录（自动处理路径分隔符）
    config['output_dir'].mkdir(parents=True, exist_ok=True)

    # ================== 模型初始化 ==================
    # 加载模型（兼容相对/绝对路径）
    model = YOLO(config['pretrained_model']) if Path(config['pretrained_model']).exists() else YOLO('yolov8s.pt')
    
    # 打印模型信息（调试用）
    model.info(verbose=True)

    # ================== 训练配置 ==================
    # 基础参数（不可被覆盖）
    base_params = {
        'data': str(config['data_yaml']),
        'project': str(config['output_dir']),
        'name': 'garbage_detect',
        'device': config['device'],
        'exist_ok': True,
        'pretrained': True
    }

    # 允许自定义的参数白名单
    train_allowlist = [
        'epochs', 'batch', 'imgsz', 'optimizer',
        'lr0', 'lrf', 'cos_lr', 'patience',
        'label_smoothing', 'dropout'
    ]

    # 安全合并参数
    train_params = {**base_params,**{k: v for k, v in config['train_params'].items() if k in train_allowlist}}

    # 添加设备相关参数
    train_params['device'] = config['device']

    # ================== 执行训练 ==================
    results = model.train(**train_params)

    # ================== 模型验证 ==================
    # 加载最佳模型（自动从训练目录获取）
    best_model_path = Path(results.save_dir) / 'weights' / 'best.pt'
    best_model = YOLO(str(best_model_path))

    # 验证集评估（自动执行）
    val_metrics = best_model.val()  # 默认使用yaml中的val集

    # 测试集评估（新增核心功能）
    test_metrics = best_model.val(
        split='test',               # ✨ 显式指定测试集
        name='garbage_test',        # 测试结果单独保存
        save_json=True,             # 生成metrics.json
        save_hybrid=True            # 保存混合标签结果
    )

    # ================== 结果输出 ==================
    print("\n[最终评估报告]")
    print(f"验证集 mAP50-95: {val_metrics.box.map:.4f}")
    print(f"测试集 mAP50-95: {test_metrics.box.map:.4f}")
    print(f"详细报告保存至: {Path(test_metrics.save_dir).resolve()}")

    # ================== 预测示例 ==================
    # 测试集预测（保存带标注的图片）
    test_pred = best_model.predict(
        source=Path(config['data_yaml']).parent / 'images/test',  # 自动解析数据集路径
        save=True,
        save_txt=True,
        save_conf=True,    # 保存置信度
        name='garbage_predict'
    )

    # 打印首个预测结果路径（调试用）
    if test_pred:
        print(f"\n预测结果示例: {Path(test_pred[0].save_dir).resolve()}/image0.jpg")

if __name__ == '__main__':
    main()