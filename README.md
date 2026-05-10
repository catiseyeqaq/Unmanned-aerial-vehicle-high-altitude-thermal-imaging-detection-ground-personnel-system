<div align="center">

# UAV High-Altitude Thermal Imaging Ground Personnel Detection System

**基于改进 YOLO11 的无人机高空热成像地面人员检测系统**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![Ultralytics](https://img.shields.io/badge/Ultralytics-8.4.8-0051ff.svg)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/License-AGPL--3.0-green.svg)](LICENSE)

</div>

## 项目简介

本项目针对**无人机高空热成像场景下的地面人员检测**任务，基于 Ultralytics YOLO11 框架提出了改进的 **YOLO11s-BSE** 模型。该模型在热红外图像中实现了对地面人员的高精度检测，适用于搜救、安防监控、灾害响应等应用场景。

同时，项目还包含面向**旋转目标检测（OBB）** 的模型变体，支持车轮、车辙等细长目标的旋转框检测。

## 核心创新

### YOLO11s-BSE 热成像检测模型

在标准 YOLO11s 的基础上，进行了以下关键改进：

| 改进模块 | 作用 | 说明 |
|---------|------|------|
| **SPDConv** | 保留细节下采样 | 空间→深度重排 + 非跨步 3×3 卷积，替代步长为 2 的常规下采样，避免热成像小目标信息丢失 |
| **EdgeEnhancement** | 边缘增强 | 强化热成像中人员轮廓的边缘特征 |
| **BiFPN** | 双向特征融合 | 可学习权重的双向特征金字塔网络，替代传统 FPN 的单向融合 |
| **CARAFE** | 内容感知上采样 | 基于内容自适应的上采样算子，比最近邻插值保留更多空间细节 |
| **EMA** | 高效混合注意力 | 分组通道 + 空间注意力机制，增强关键区域响应 |
| **CoordinateAttention** | 坐标注意力 | 捕获水平和垂直方向的长程依赖 |
| **SimAM** | 无参数注意力 | 基于 3D 能量函数的注意力机制，零额外参数 |
| **P2 检测层** | 小目标检测 | 增加 1/4 分辨率的 P2 检测头，专门针对高空热成像中的微小人员目标 |
| **NWD 损失** | 小目标优化 | Normalized Wasserstein Distance 损失，替代 IoU 度量，更适合极小目标的回归 |

### 模型架构示意

```
输入 (1024×1024 热红外图像)
    │
    ▼
┌─────────────────────────────────────────────┐
│  Backbone (主干网络)                         │
│  Conv → SPDConv → C3k2 → EdgeEnhancement   │
│  → SPDConv → C3k2 → SPDConv → C3k2         │
│  → SPDConv → C3k2 → SPPF → C2PSA           │
│                                             │
│  输出: P2(128ch), P3(256ch), P4(512ch), P5(1024ch)  │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  Neck (双向特征金字塔)                       │
│  Top-down: CARAFE + BiFPNAdd + EMA         │
│  Bottom-up: Conv + BiFPNAdd + SimAM        │
│  + CoordinateAttention                      │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  Detection Head (P2, P3, P4, P5 四尺度)     │
│  + NWD Loss (小目标优化)                     │
└─────────────────────────────────────────────┘
```

## 性能指标

| 模型 | 任务 | mAP50 | mAP50-95 | 输入尺寸 |
|------|------|-------|----------|---------|
| **YOLO11s-BSE** | 热成像人员检测 | **0.94** | **0.94** | 1024 |
| YOLO11s-CBSE3 | 热成像人员检测 (精简版) | 0.88 | 0.43 | 1024 |
| YOLO11-obb | OBB 旋转框检测 | 0.57 | 0.41 | 640 |

## 项目结构

```
├── train_yolo11热成像.py      # 热成像人员检测训练脚本 (核心)
├── train_obb.py               # OBB 旋转框检测训练脚本
├── train_FFS.py               # SPDConv+DSConv OBB 训练
├── train_yolo11.py            # 标准 YOLO11 检测
├── train_yolo26.py            # YOLO26 检测
├── train_yolo26-OBB.py        # YOLO26 旋转框检测
├── train_obbDSConv.py         # DSConv 改进 OBB
├── train_obbFasterNet.py      # FasterNet 改进 OBB
├── train_obbSPDCnov.py        # SPDConv 改进 OBB
├── yolo11s_BSE.yaml           # YOLO11s-BSE 模型配置 (核心)
├── yolofinally.yaml           # SPDConv+DSConv OBB 模型配置
├── yolo11n.yaml               # 标准 YOLO11n 配置
├── 热成像/                     # 热成像数据集
│   ├── data.yaml              # 数据集配置
│   └── classes.txt            # 类别定义 (people)
├── ultralytics/               # 框架代码 (含自定义模块)
│   └── nn/Attention/          # 自定义注意力与特征融合模块
│       ├── SPDConv.py         # 空间-深度卷积
│       ├── BiFPN.py           # 双向特征金字塔网络
│       ├── EMA.py             # 高效混合注意力
│       ├── CARAFE.py          # 内容感知上采样
│       ├── SimAM.py           # 无参数注意力
│       ├── DSConv.py          # 可变形稀疏卷积
│       └── FasterNet.py       # 轻量网络
├── requirements.txt           # 项目依赖
└── paper_assets/              # 论文相关资源
```

## 环境配置

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| GPU | NVIDIA GTX 1060 6GB | NVIDIA RTX 3060+ / RTX 5060 8GB |
| 内存 | 16 GB | 32 GB |
| 存储 | 10 GB 可用空间 | SSD 50GB+ |

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/catiseyeqaq/Unmanned-aerial-vehicle-high-altitude-thermal-imaging-detection-ground-personnel-system.git
cd Unmanned-aerial-vehicle-high-altitude-thermal-imaging-detection-ground-personnel-system

# 2. 创建虚拟环境
conda create -n thermal python=3.10 -y
conda activate thermal

# 3. 安装 PyTorch (CUDA 版本)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 4. 安装项目依赖
pip install -r requirements.txt
```

## 快速开始

### 训练热成像检测模型

```bash
python train_yolo11热成像.py
```

### 推理预测

```python
from ultralytics import YOLO
from pathlib import Path

root = Path(__file__).resolve().parent
model = YOLO(str(root / "runs" / "热成像" / "yolo11s-BSE" / "weights" / "best.pt"))

results = model("path/to/thermal_image.jpg", conf=0.25, iou=0.7)
results[0].show()
```

### 模型导出 (部署)

```python
# 导出 ONNX
model.export(format="onnx", imgsz=1024)

# 导出 TensorRT (NVIDIA GPU)
model.export(format="engine", imgsz=1024, half=True)
```

## 训练超参数

| 参数 | 热成像模型 | OBB 模型 |
|------|----------|---------|
| 输入尺寸 | 1024 | 640 |
| 批次大小 | 2 | 32 |
| 优化器 | AdamW | AdamW |
| 初始学习率 | 0.0005 | 0.0001 |
| 轮数 | 100 | 200 |
| Box Loss 权重 | 11.0 | 7.5 |
| Mosaic 增强 | 0.3 (低) | 1.0 (强) |
| NWD Loss | 开启 | 关闭 |

## 自定义模块清单

| 模块 | 源码 | 说明 |
|------|------|------|
| SPDConv | `ultralytics/nn/Attention/SPDConv.py` | PixelUnshuffle + 非跨步卷积，替代步长 2 下采样 |
| BiFPNAdd2/3 | `ultralytics/nn/Attention/BiFPN.py` | 双向 FPN 动态权重融合，ReLU + L1 归一化 |
| EMA | `ultralytics/nn/Attention/EMA.py` | 分组通道 + 空间混合注意力 |
| CoordinateAttention | `ultralytics/nn/modules/ca_ee.py` | 水平+垂直方向坐标注意力 |
| SimAM | `ultralytics/nn/Attention/SimAM.py` | 基于 3D 能量函数的无参数注意力 |
| CARAFE | `ultralytics/nn/Attention/CARAFE.py` | 内容感知自适应上采样 |
| EdgeEnhancement | `ultralytics/nn/modules/ca_ee.py` | 边缘增强模块 |
| DSConv | `ultralytics/nn/Attention/DSConv.py` | 可变形稀疏卷积 |
| FasterNet | `ultralytics/nn/Attention/FasterNet.py` | 部分卷积轻量网络 |

## 引用

如果本项目对您的研究有帮助，请引用：

```bibtex
@software{uav_thermal_detection,
  title={UAV High-Altitude Thermal Imaging Ground Personnel Detection System},
  author={catiseyeqaq},
  year={2025},
  url={https://github.com/catiseyeqaq/Unmanned-aerial-vehicle-high-altitude-thermal-imaging-detection-ground-personnel-system}
}
```

## 致谢

- [Ultralytics](https://github.com/ultralytics/ultralytics) - YOLO 系列框架
- [BiFPN](https://arxiv.org/abs/1911.09070) - EfficientDet 双向特征金字塔
- [CARAFE](https://arxiv.org/abs/1905.02188) - 内容感知上采样
- [SPDConv](https://arxiv.org/abs/2208.03641) - 空间到深度卷积

## 许可证

本项目基于 [AGPL-3.0](LICENSE) 许可证开源。
