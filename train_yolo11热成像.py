from pathlib import Path

from ultralytics import YOLO

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    model_cfg = root / "yolo11s_BSE.yaml"
    data_cfg = root / "热成像" / "data.yaml"
    project_dir = root / "runs"

    if not model_cfg.exists():
        raise FileNotFoundError(f"模型配置不存在: {model_cfg}")
    if not data_cfg.exists():
        raise FileNotFoundError(f"数据配置不存在: {data_cfg}")

    model = YOLO(str(model_cfg))
    train_results = model.train(
        data=str(data_cfg),
        epochs=100,
        patience=40,
        batch=2,
        imgsz=1024,
        device=0,
        workers=1,
        project=str(project_dir),
        name="yolo11s-CBSE3",
        optimizer="AdamW",
        lr0=0.0005,
        lrf=0.01,
        momentum=0.9,
        weight_decay=0.0005,
        cos_lr=True,
        warmup_epochs=4.0,
        warmup_bias_lr=0.02,
        box=11.0,
        cls=0.5,
        dfl=2.2,
        nwd=True,
        hsv_h=0.0,
        hsv_s=0.0,
        hsv_v=0.3,
        degrees=10.0,
        translate=0.02,
        scale=0.2,
        flipud=0.3,
        fliplr=0.5,
        mosaic=0.3,
        copy_paste=0.1,
        close_mosaic=50,
        cache=True,
        single_cls=False,
        deterministic=True,
        seed=0,
        amp=True,
        val=True,
        plots=True,
    )
