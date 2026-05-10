import torch
import torch.nn as nn


class CoordinateAttention(nn.Module):
    """Coordinate Attention for small object detection.

    Captures long-range dependencies along spatial directions while preserving precise positional information. More
    effective than SE/CBAM for small targets.

    Reference: TY-RIST (ICCV 2025 Workshop), Hou et al. "Coordinate Attention for Efficient Mobile Network Design"
    """

    def __init__(self, inp: int, reduction: int = 32):
        """
        Args:
            inp: Input channels
            reduction: Reduction ratio for attention bottleneck.
        """
        super().__init__()
        self.pool_h = nn.AdaptiveAvgPool2d((None, 1))
        self.pool_w = nn.AdaptiveAvgPool2d((1, None))

        mip = max(8, inp // reduction)

        self.conv1 = nn.Conv2d(inp, mip, kernel_size=1, stride=1, padding=0)
        self.bn1 = nn.BatchNorm2d(mip)
        self.act = nn.SiLU()

        self.conv_h = nn.Conv2d(mip, inp, kernel_size=1, stride=1, padding=0)
        self.conv_w = nn.Conv2d(mip, inp, kernel_size=1, stride=1, padding=0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        identity = x

        _n, _c, h, w = x.size()
        x_h = self.pool_h(x)
        x_w = self.pool_w(x).permute(0, 1, 3, 2)

        y = torch.cat([x_h, x_w], dim=2)
        y = self.conv1(y)
        y = self.bn1(y)
        y = self.act(y)

        x_h, x_w = torch.split(y, [h, w], dim=2)
        x_w = x_w.permute(0, 1, 3, 2)

        a_h = self.conv_h(x_h).sigmoid()
        a_w = self.conv_w(x_w).sigmoid()

        out = identity * a_w * a_h

        return out


class EdgeEnhancement(nn.Module):
    """Edge Enhancement module for thermal imaging.

    Uses low-frequency suppression and high-frequency enhancement strategy to improve edge feature extraction for small
    targets in thermal images.

    Reference: AFDPN (JERA 2024), PLOS ONE 2025
    """

    def __init__(self, inp: int):
        """
        Args:
            inp: Input channels.
        """
        super().__init__()
        self.conv1 = nn.Conv2d(inp, inp, kernel_size=3, padding=1, groups=inp, bias=False)
        self.bn1 = nn.BatchNorm2d(inp)
        self.act = nn.SiLU()

        self.sobel_x = nn.Conv2d(inp, inp, kernel_size=3, padding=1, groups=inp, bias=False)
        self.sobel_y = nn.Conv2d(inp, inp, kernel_size=3, padding=1, groups=inp, bias=False)

        self.init_sobel_kernels()

        self.conv_out = nn.Conv2d(inp * 2, inp, kernel_size=1, bias=False)
        self.bn_out = nn.BatchNorm2d(inp)

    def init_sobel_kernels(self):
        """Initialize Sobel kernels for edge detection."""
        sobel_x_kernel = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=torch.float32).view(1, 1, 3, 3)

        sobel_y_kernel = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=torch.float32).view(1, 1, 3, 3)

        with torch.no_grad():
            self.sobel_x.weight.copy_(sobel_x_kernel.repeat(self.sobel_x.weight.shape[0], 1, 1, 1))
            self.sobel_y.weight.copy_(sobel_y_kernel.repeat(self.sobel_y.weight.shape[0], 1, 1, 1))
            self.sobel_x.requires_grad_(False)
            self.sobel_y.requires_grad_(False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        identity = x

        edge_x = self.sobel_x(x)
        edge_y = self.sobel_y(x)
        edge = torch.sqrt(edge_x.pow(2) + edge_y.pow(2) + 1e-8)

        x_smooth = self.conv1(x)
        x_smooth = self.bn1(x_smooth)
        x_smooth = self.act(x_smooth)

        x_enhanced = torch.cat([x_smooth, edge], dim=1)
        x_enhanced = self.conv_out(x_enhanced)
        x_enhanced = self.bn_out(x_enhanced)

        out = x_enhanced + identity

        return self.act(out)
