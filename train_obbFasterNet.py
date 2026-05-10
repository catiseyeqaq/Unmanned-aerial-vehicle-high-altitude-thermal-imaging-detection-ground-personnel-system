from pathlib import Path

from ultralytics import YOLO

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    model_cfg = root / "yolo11-obbFasterNet.yaml"
    data_cfg = root / "carweel_yolo11_obb" / "data.yaml"
    project_dir = root / "runs"
    model = YOLO(str(model_cfg))
    train_results = model.train(
        # --- 基础配置 ---
        data=str(data_cfg),
        epochs=200,  # 增加 Epoch 以配合强数据增强
        patience=20,  # 早停机制 (Early Stopping)，防止过拟合
        batch=32,  # 批次大小
        imgsz=640,  # 输入尺寸
        device=0,
        workers=4,  # 增加 Worker 数量，提升数据加载并行度
        project=str(project_dir),
        name="yolo11n_OBB_FasterNet",
        # --- 优化策略 (Optimization) ---
        optimizer="AdamW",  # 固定优化器，避免auto覆盖手动学习率
        lr0=0.0001,  # 进一步降低初始学习率
        lrf=0.001,  # 略提高最终学习率比例，避免后期过早收敛
        momentum=0.9,  # 保持动量
        pretrained=True,  # 启用预训练权重，提升泛化能力
        cos_lr=True,  # 余弦退火
        warmup_epochs=6.0,  # 保持较长Warm-up，减少早中期振荡
        warmup_bias_lr=0.02,
        weight_decay=0.0005,  # 保持正则化系数
        # --- 损失函数优化 (Loss) ---
        box=7.5,  # Box Loss Gain
        cls=0.5,  # Class Loss Gain
        dfl=1.5,  # DFL 权重
        # --- 数据增强 (Data Augmentation) - 严格控制：强旋转，无尺度变化 ---
        # 1. 光照与环境适应
        hsv_h=0.015,  # 色调微调
        hsv_s=0.2,  # 饱和度微调
        hsv_v=0.35,  # 增强亮度扰动
        # 2. 几何变换 (最大化旋转，严格禁止缩放/平移)
        degrees=90.0,  # [增大] 最大化旋转范围 (+/- 90度)，全方位覆盖
        translate=0.05,  # 小幅平移增强
        scale=0.25,  # 适度缩放增强
        shear=1.0,  # 轻量剪切增强
        perspective=0.0003,  # 轻量透视扰动
        # 3. 翻转
        flipud=0.5,  # 垂直翻转
        fliplr=0.5,  # 水平翻转
        # 4. 高级增强
        mosaic=1.0,  # [开启] Mosaic 增强
        mixup=0.08,  # 轻量 Mixup 提升鲁棒性
        copy_paste=0.0,  # 关闭
        close_mosaic=15,
        erasing=0.2,
        seed=0,
        deterministic=True,
        amp=True,
        resume=False,
        # --- 验证与测试 ---
        val=True,  # 训练期间进行验证
        plots=True,  # 保存训练曲线和可视化结果
    )
