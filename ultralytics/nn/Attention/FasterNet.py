import torch
import torch.nn as nn

class PartialConv(nn.Module):
    def __init__(self, c1, c2, kernel_size=3, stride=1, padding=1, n_div=4, forward="split_cat"):
        super().__init__()
        if c1 <= 1:
            dim_conv = 1
        else:
            dim_conv = max(1, min(c1 - 1, c1 // n_div))
        self.dim_conv = dim_conv
        self.dim_untouched = c1 - dim_conv
        self.partial_conv = nn.Conv2d(
            self.dim_conv,
            self.dim_conv,
            kernel_size,
            stride,
            padding,
            bias=False,
        )
        if c1 != c2:
            self.proj = nn.Conv2d(c1, c2, 1, bias=False)
        else:
            self.proj = nn.Identity()
        self.forward_type = forward

    def forward(self, x):
        if self.dim_untouched == 0:
            x = self.partial_conv(x)
        elif self.forward_type == "split_cat":
            x1, x2 = torch.split(x, [self.dim_conv, self.dim_untouched], dim=1)
            x1 = self.partial_conv(x1)
            x = torch.cat((x1, x2), dim=1)
        else:
            y = x.clone()
            y[:, : self.dim_conv] = self.partial_conv(y[:, : self.dim_conv])
            x = y
        return self.proj(x)


class FasterNetBlock(nn.Module):
    def __init__(self, c1, c2=None, n_div=4, mlp_ratio=2.0, drop_path=0.0, act_layer=nn.GELU, layer_scale=1e-6):
        super().__init__()
        c2 = c2 or c1
        mlp_hidden_dim = max(int(c2 * mlp_ratio), c2)
        self.token_mixer = PartialConv(c1, c1, kernel_size=3, padding=1, n_div=n_div)
        self.norm = nn.BatchNorm2d(c1)
        self.mlp = nn.Sequential(
            nn.Conv2d(c1, mlp_hidden_dim, 1, bias=False),
            nn.BatchNorm2d(mlp_hidden_dim),
            act_layer(),
            nn.Conv2d(mlp_hidden_dim, c2, 1, bias=False),
            nn.BatchNorm2d(c2),
        )
        self.drop_path = DropPath(drop_path) if drop_path > 0. else nn.Identity()
        if c1 != c2:
            self.shortcut = nn.Sequential(
                nn.Conv2d(c1, c2, 1, bias=False),
                nn.BatchNorm2d(c2),
            )
        else:
            self.shortcut = nn.Identity()
        self.gamma = nn.Parameter(layer_scale * torch.ones(1, c2, 1, 1)) if layer_scale > 0 else None

    def forward(self, x):
        shortcut = self.shortcut(x)
        x = self.token_mixer(x)
        x = self.norm(x)
        x = self.mlp(x)
        if self.gamma is not None:
            x = x * self.gamma
        return shortcut + self.drop_path(x)


class FasterNetStage(nn.Module):
    def __init__(self, c1, c2, depth=2, n_div=4, mlp_ratio=2.0, drop_path=0.0):
        super().__init__()
        self.downsample = nn.Sequential(
            nn.Conv2d(c1, c2, kernel_size=2, stride=2, bias=False),
            nn.BatchNorm2d(c2),
        )
        rates = torch.linspace(0, drop_path, steps=max(depth, 1)).tolist()
        self.blocks = nn.Sequential(
            *[FasterNetBlock(c2, c2, n_div=n_div, mlp_ratio=mlp_ratio, drop_path=rates[i]) for i in range(depth)]
        )

    def forward(self, x):
        x = self.downsample(x)
        x = self.blocks(x)
        return x


class DropPath(nn.Module):
    def __init__(self, drop_prob=0.0):
        super().__init__()
        self.drop_prob = drop_prob

    def forward(self, x):
        if self.drop_prob == 0.0 or not self.training:
            return x
        keep_prob = 1 - self.drop_prob
        shape = (x.shape[0],) + (1,) * (x.ndim - 1)
        random_tensor = keep_prob + torch.rand(shape, dtype=x.dtype, device=x.device)
        random_tensor.floor_()
        return x.div(keep_prob) * random_tensor
