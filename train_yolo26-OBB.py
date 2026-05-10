from pathlib import Path
from ultralytics import YOLO

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    model_cfg = root / "ultralytics" / "cfg" / "models" / "26" / "yolo26-obb.yaml"
    data_cfg = root / "carweel_yolo11_obb" / "data.yaml"
    project_dir = root / "runs"
    model = YOLO(str(model_cfg))
    train_results = model.train(
        data=str(data_cfg),
        epochs=200,
        patience=30,
        batch=32,
        imgsz=640,
        device=0,
        workers=8,
        project=str(project_dir),
        name="yolo26n",
        optimizer="AdamW",
        lr0=0.0001,
        lrf=0.002,
        momentum=0.9,
        pretrained=False,
        cos_lr=True,
        warmup_epochs=6.0,
        warmup_bias_lr=0.02,
        weight_decay=0.0005,
        box=7.5,
        cls=0.5,
        dfl=1.5,
        hsv_h=0.015,
        hsv_s=0.2,
        hsv_v=0.35,
        degrees=90.0,
        translate=0.05,
        scale=0.25,
        shear=1.0,
        perspective=0.0003,
        flipud=0.5,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.08,
        copy_paste=0.0,
        close_mosaic=15,
        erasing=0.2,
        seed=0,
        deterministic=True,
        amp=True,
        resume=False,
        val=True,
        plots=True,
    )
