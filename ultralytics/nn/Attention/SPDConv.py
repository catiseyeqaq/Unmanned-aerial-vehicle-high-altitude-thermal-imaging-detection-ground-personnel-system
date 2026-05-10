import torch
import torch.nn as nn
import torch.nn.functional as F


class SPDConv(nn.Module):
    def __init__(self, c1, c2, dimension=1, kernel_size=3):
        super().__init__()
        self.dimension = dimension
        p = kernel_size // 2
        self.space_to_depth = nn.PixelUnshuffle(2)
        self.conv = nn.Conv2d(c1 * 4, c2, kernel_size, 1, p, bias=False)
        self.bn = nn.BatchNorm2d(c2)
        self.act = nn.SiLU()

    def forward(self, x):
        _, _, h, w = x.shape
        pad_h = h % 2
        pad_w = w % 2
        if pad_h or pad_w:
            x = F.pad(x, (0, pad_w, 0, pad_h), mode="replicate")
        x = self.space_to_depth(x)
        return self.act(self.bn(self.conv(x)))
