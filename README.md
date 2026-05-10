# UAV High-Altitude Thermal Imaging Ground Personnel Detection System

基于改进 YOLO11 的无人机高空热成像地面人员检测系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-AGPL--3.0-green.svg)](LICENSE)

## 简介

针对无人机高空热成像场景，提出改进的 **YOLO11s-BSE** 模型，在标准 YOLO11s 基础上引入 SPDConv + BiFPN + EMA + CARAFE + SimAM + CoordinateAttention + EdgeEnhancement，并增加 P2 小目标检测层和 NWD Loss，实现对地面人员的高精度检测。

## 模型架构

```
输入 (1024×1024 热红外图像)
  → Backbone: Conv → SPDConv → C3k2 → EdgeEnhancement → SPDConv → C3k2 → SPDConv → C3k2 → SPDConv → C3k2 → SPPF → C2PSA
  → Neck: BiFPN + CARAFE + EMA + CoordinateAttention + SimAM
  → Head: Detect(P2, P3, P4, P5) + NWD Loss
```

## 性能

| 模型             | mAP50    | mAP50-95 | imgsz |
| ---------------- | -------- | -------- | ----- |
| **YOLO11s-BSE**  | **0.94** | **0.94** | 1024  |
| YOLO11s-CBSE3    | 0.88     | 0.43     | 1024  |
| YOLO11-obb (OBB) | 0.57     | 0.41     | 640   |

## 快速开始

```bash
git clone https://github.com/catiseyeqaq/Unmanned-aerial-vehicle-high-altitude-thermal-imaging-detection-ground-personnel-system.git
cd Unmanned-aerial-vehicle-high-altitude-thermal-imaging-detection-ground-personnel-system

conda create -n thermal python=3.10 -y && conda activate thermal
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
```

**训练**

```bash
python train_yolo11热成像.py
```

**推理**

```python
from ultralytics import YOLO

model = YOLO("runs/热成像/yolo11s-BSE/weights/best.pt")
results = model("thermal_image.jpg", conf=0.25, iou=0.7)
results[0].show()
```

**导出**

```python
model.export(format="onnx", imgsz=1024)  # ONNX
model.export(format="engine", imgsz=1024)  # TensorRT
```

## 许可证

[AGPL-3.0](LICENSE)
