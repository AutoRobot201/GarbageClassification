"""
YOLOv11 垃圾检测训练脚本 (适配新版数据集结构)
    修改说明：
    1. 移除测试集相关代码
    2. 适配 train/images + train/labels 结构
    3. 增强路径兼容性处理
"""
from ultralytics import YOLO
import torch
import os
from pathlib import Path
import argparse

def validate_structure(data_path):
    """验证数据集结构是否符合要求"""
    required = {
        'train': ['images', 'labels'],
        'val': ['images', 'labels']
    }
    
    missing = []
    for split in required:
        split_path = Path(data_path) / split
        if not split_path.exists():
            missing.append(f"缺失目录: {split_path}")
            continue
            
        for sub in required[split]:
            if not (split_path / sub).exists():
                missing.append(f"缺失子目录: {split_path/sub}")
    
    if missing:
        raise FileNotFoundError("\n".join(missing))

def main():
    # ================== 配置参数 ==================
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', action='store_true', help='继续训练')
    args = parser.parse_args()
    
    config = {
        # 数据集配置
        'data_yaml': Path('E:/Code/NJUST-AutoRobot/GarbageClassification/Code/dev_2.0/garbage_ylj.yaml'),
        'dataset_root': Path("E:\\Code\\NJUST-AutoRobot\\GarbageClassification\\Dataset\\mix_data_20250417"),
        
        # 模型配置
        'pretrained_model': 'yolov8s.pt' if not args.resume else '',  # 自动处理继续训练
        'output_dir': Path('runs/train'),  # 输出目录
        
        # 训练超参数
        'train_params': {
            'epochs': 100,
            'batch': 16,
            'imgsz': 640,
            'optimizer': 'AdamW',
            'lr0': 1e-3,
            'cos_lr': True,
            'patience': 30,
            'resume': args.resume  # 命令行参数传递
        }
    }

    # ================== 预处理 ==================
    # 验证数据集结构
    validate_structure(config['dataset_root'])
    
    # 设备配置
    config['device'] = '0' if torch.cuda.is_available() else 'cpu'
    
    # 创建输出目录
    config['output_dir'].mkdir(parents=True, exist_ok=True)

    # ================== 模型初始化 ==================
    model = YOLO(config['pretrained_model']) if not args.resume else YOLO('E:\\Code\\NJUST-AutoRobot\\GarbageClassification\\runs\\train\\garbage_v1\\weights\\last.pt')
    
    # 打印模型信息
    print("\n" + "="*40)
    model.info(verbose=True)
    print("="*40 + "\n")

    # ================== 训练配置 ==================
    train_params = {
        'data': str(config['data_yaml']),
        'project': str(config['output_dir']),
        'name': 'garbage_mix_YOLOv8s_ep100_batch16',
        'device': config['device'],
        'exist_ok': True,
        'pretrained': not args.resume,
        **config['train_params']
    }

    # ================== 执行训练 ==================
    results = model.train(**train_params)

    # ================== 模型验证 ==================
    best_model = YOLO(Path(results.save_dir) / 'weights' / 'best.pt')
    
    # 验证集评估
    val_metrics = best_model.val(
        data=str(config['data_yaml']),
        split='val',
        name='final_val',
        save_json=True
    )

    # ================== 结果报告 ==================
    print("\n[训练报告]")
    print(f"验证集精度: mAP50-95 = {val_metrics.box.map:.4f}")
    print(f"最佳模型路径: {Path(results.save_dir)/'weights'/'best.pt'}")
    print(f"训练日志: {Path(results.save_dir)/'results.csv'}")

    # ================== 预测示例 ==================
    demo_pred = best_model.predict(
        source=config['dataset_root']/'val'/'images',
        save=True,
        save_txt=True,
        conf=0.5,
        name='demo_predict'
    )
    
    if demo_pred:
        print(f"\n预测示例保存至: {Path(demo_pred[0].save_dir).resolve()}")

if __name__ == '__main__':
    main()