from ultralytics import YOLO

# 加载预训练的 YOLO11n-OBB 模型
model = YOLO("yolo11n-obb.pt")

# 训练模型 - GTX 1650 4GB显存优化配置
train_results = model.train(
    # 基础配置
    data="coco8.yaml",  # 数据集配置文件路径
    epochs=200,  # 训练轮数
    imgsz=640,  # 输入图像大小
    batch=8,  # 批次大小（显存不足可改为4）
    device=0,  # 使用GPU 0
    
    # 学习率设置
    lr0=0.01,  # 初始学习率
    lrf=0.01,  # 最终学习率系数（最终学习率 = lr0 * lrf）
    warmup_epochs=3.0,  # 学习率预热轮数
    
    # 早停机制
    patience=50,  # 50轮无改善则停止训练
    
    # 性能优化
    amp=False,  # 混合精度训练,1650不支持（节省显存，加速训练）
    workers=2,  # 数据加载线程数
    
    # 保存设置
    project="runs/train",  # 项目保存路径
    name="yolo11n_obb_exp",  # 实验名称
)