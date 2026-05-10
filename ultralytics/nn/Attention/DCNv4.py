import torch
import torch.nn as nn
import torch.nn.functional as F
from contextlib import nullcontext
import platform

try:
    from torchvision.ops import deform_conv2d
    _HAS_DEFORM = True
except Exception:
    deform_conv2d = None
    _HAS_DEFORM = False

if platform.system() == "Windows":
    _HAS_DEFORM = False


class DCNv4(nn.Module):
    def __init__(
        self,
        c1,
        c2,
        kernel_size=3,
        stride=1,
        padding=1,
        dilation=1,
        groups=1,
        offset_groups=1,
    ):
        super().__init__()
        self.c1 = c1
        self.c2 = c2
        self.kernel_size = kernel_size
        self.stride = stride if isinstance(stride, tuple) else (stride, stride)
        self.padding = padding if isinstance(padding, tuple) else (padding, padding)
        self.dilation = dilation if isinstance(dilation, tuple) else (dilation, dilation)
        self.groups = groups
        self.offset_groups = offset_groups

        self.offset = nn.Conv2d(
            c1,
            2 * offset_groups * kernel_size * kernel_size,
            kernel_size=kernel_size,
            stride=self.stride,
            padding=self.padding,
            dilation=self.dilation,
            bias=True,
        )
        self.mask = nn.Conv2d(
            c1,
            offset_groups * kernel_size * kernel_size,
            kernel_size=kernel_size,
            stride=self.stride,
            padding=self.padding,
            dilation=self.dilation,
            bias=True,
        )

        self.weight = nn.Parameter(torch.empty(c2, c1 // groups, kernel_size, kernel_size))
        self.bias = nn.Parameter(torch.zeros(c2))

        self.bn = nn.BatchNorm2d(c2)
        self.act = nn.SiLU()

        nn.init.kaiming_uniform_(self.weight, a=1.0)
        nn.init.zeros_(self.offset.weight)
        nn.init.zeros_(self.offset.bias)
        nn.init.zeros_(self.mask.weight)
        nn.init.zeros_(self.mask.bias)

    def forward(self, x):
        offset = self.offset(x)
        mask = torch.sigmoid(self.mask(x))

        if _HAS_DEFORM:
            x_dtype = x.dtype
            amp_ctx = torch.cuda.amp.autocast(enabled=False) if x.is_cuda else nullcontext()
            with amp_ctx:
                y = deform_conv2d(
                    input=x.float().contiguous(),
                    offset=offset.float().contiguous(),
                    weight=self.weight.float().contiguous(),
                    bias=self.bias.float().contiguous(),
                    stride=self.stride,
                    padding=self.padding,
                    dilation=self.dilation,
                    mask=mask.float().contiguous(),
                )
            y = y.to(x_dtype)
        else:
            y = F.conv2d(
                x,
                self.weight,
                self.bias,
                stride=self.stride,
                padding=self.padding,
                dilation=self.dilation,
                groups=self.groups,
            )
            m = F.adaptive_avg_pool2d(mask.mean(dim=1, keepdim=True), y.shape[-2:])
            y = y * m

        return self.act(self.bn(y))


class DCNv4_Fast(nn.Module):
    def __init__(self, c1, c2, kernel_size=3, stride=1):
        super().__init__()
        self.block = DCNv4(
            c1=c1,
            c2=c2,
            kernel_size=kernel_size,
            stride=stride,
            padding=kernel_size // 2,
            groups=1,
            offset_groups=1,
        )

    def forward(self, x):
        return self.block(x)
