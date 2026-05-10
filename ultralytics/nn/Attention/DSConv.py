import torch
import torch.nn as nn
import torch.nn.functional as F


class DSConv(nn.Module):
    def __init__(self, c1, c2, k=9, stride=1, extend_scope=1.0, offset_scale=0.5):
        super().__init__()
        self.k = int(k)
        self.stride = int(stride)
        self.extend_scope = float(extend_scope)
        self.offset_scale = float(offset_scale)
        hidden = max(c1 // 2, 16)
        self.offset = nn.Sequential(
            nn.Conv2d(c1, hidden, 3, stride=self.stride, padding=1, bias=False),
            nn.BatchNorm2d(hidden),
            nn.SiLU(),
            nn.Conv2d(hidden, 4 * self.k, 1, bias=True),
        )
        self.proj_x = nn.Conv2d(c1, c2, 1, bias=False)
        self.proj_y = nn.Conv2d(c1, c2, 1, bias=False)
        self.bn = nn.BatchNorm2d(c2)
        self.act = nn.SiLU()
        nn.init.zeros_(self.offset[-1].weight)
        nn.init.zeros_(self.offset[-1].bias)

    def _base_grid(self, b, h, w, device, dtype):
        ys = torch.linspace(-1.0, 1.0, h, device=device, dtype=dtype)
        xs = torch.linspace(-1.0, 1.0, w, device=device, dtype=dtype)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        base = torch.stack((gx, gy), dim=-1)
        return base.unsqueeze(0).repeat(b, 1, 1, 1)

    def _sample(self, x, offsets, horizontal=True):
        b, _c, h, w = x.shape
        base = self._base_grid(b, h, w, x.device, x.dtype)
        center = (self.k - 1) * 0.5
        out = 0.0
        step_x = 2.0 / max(w - 1, 1)
        step_y = 2.0 / max(h - 1, 1)
        off_x, off_y = torch.chunk(offsets, 2, dim=1)
        for i in range(self.k):
            dx = (i - center) * step_x if horizontal else 0.0
            dy = (i - center) * step_y if not horizontal else 0.0
            ox = off_x[:, i : i + 1].permute(0, 2, 3, 1) * self.offset_scale * self.extend_scope * step_x
            oy = off_y[:, i : i + 1].permute(0, 2, 3, 1) * self.offset_scale * self.extend_scope * step_y
            grid = base.clone()
            grid[..., 0:1] = grid[..., 0:1] + dx + ox
            grid[..., 1:2] = grid[..., 1:2] + dy + oy
            sampled = F.grid_sample(x, grid, mode="bilinear", padding_mode="border", align_corners=True)
            out = out + sampled
        return out / self.k

    def forward(self, x):
        pred = self.offset(x)
        ox, oy = torch.split(pred, [2 * self.k, 2 * self.k], dim=1)
        sx = self._sample(x, ox, horizontal=True)
        sy = self._sample(x, oy, horizontal=False)
        out = self.proj_x(sx) + self.proj_y(sy)
        return self.act(self.bn(out))
