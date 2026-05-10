import torch
import torch.nn as nn
import torch.nn.functional as F


class StarBlock(nn.Module):
    def __init__(self, c1, c2, kernel_size=7, mlp_ratio=2.0, dropout=0.0, layer_scale=1e-6):
        super().__init__()
        hidden = max(int(c2 * mlp_ratio), c2)
        self.dw = nn.Conv2d(c1, c1, kernel_size, 1, kernel_size // 2, groups=c1, bias=False)
        self.dw_bn = nn.BatchNorm2d(c1)
        self.f1 = nn.Conv2d(c1, hidden, 1, bias=False)
        self.f2 = nn.Conv2d(c1, hidden, 1, bias=False)
        self.proj = nn.Conv2d(hidden, c2, 1, bias=False)
        self.proj_bn = nn.BatchNorm2d(c2)
        self.act = nn.ReLU6(inplace=True)
        self.drop = nn.Dropout(dropout) if dropout > 0 else nn.Identity()
        self.shortcut = nn.Identity() if c1 == c2 else nn.Sequential(nn.Conv2d(c1, c2, 1, bias=False), nn.BatchNorm2d(c2))
        self.gamma = nn.Parameter(layer_scale * torch.ones(1, c2, 1, 1)) if layer_scale > 0 else None

    def forward(self, x):
        residual = self.shortcut(x)
        x = self.dw_bn(self.dw(x))
        x = self.act(self.f1(x)) * self.f2(x)
        x = self.proj_bn(self.proj(x))
        if self.gamma is not None:
            x = x * self.gamma
        x = self.drop(x)
        return residual + x
