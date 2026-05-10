import torch
import torch.nn as nn
import torch.nn.functional as F


class EMA(nn.Module):
    def __init__(self, channels, factor=8, eps=1e-6):
        super().__init__()
        self.groups = int(factor)
        if channels % self.groups != 0:
            raise ValueError(f"channels({channels}) must be divisible by factor({self.groups})")
        self.group_channels = channels // self.groups
        self.eps = eps
        self.softmax = nn.Softmax(-1)
        self.agp = nn.AdaptiveAvgPool2d((1, 1))
        self.pool_h = nn.AdaptiveAvgPool2d((None, 1))
        self.pool_w = nn.AdaptiveAvgPool2d((1, None))
        self.gn = nn.GroupNorm(self.group_channels, self.group_channels, eps=self.eps)
        self.conv1x1 = nn.Conv2d(self.group_channels, self.group_channels, kernel_size=1, stride=1, padding=0, bias=True)
        self.conv3x3 = nn.Conv2d(self.group_channels, self.group_channels, kernel_size=3, stride=1, padding=1, bias=True)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        b, c, h, w = x.size()
        group_x = x.reshape(b * self.groups, self.group_channels, h, w)
        x_h = self.pool_h(group_x)
        x_w = self.pool_w(group_x).permute(0, 1, 3, 2)
        hw = self.conv1x1(torch.cat([x_h, x_w], dim=2))
        x_h, x_w = torch.split(hw, [h, w], dim=2)
        x1 = self.gn(group_x * self.sigmoid(x_h) * self.sigmoid(x_w.permute(0, 1, 3, 2)))
        x2 = self.conv3x3(group_x)
        x11 = self.softmax(self.agp(x1).reshape(b * self.groups, -1, 1).permute(0, 2, 1))
        x12 = x2.reshape(b * self.groups, self.group_channels, -1)
        x21 = self.softmax(self.agp(x2).reshape(b * self.groups, -1, 1).permute(0, 2, 1))
        x22 = x1.reshape(b * self.groups, self.group_channels, -1)
        weights = (torch.matmul(x11, x12) + torch.matmul(x21, x22)).reshape(b * self.groups, 1, h, w)
        return (group_x * self.sigmoid(weights)).reshape(b, c, h, w)
