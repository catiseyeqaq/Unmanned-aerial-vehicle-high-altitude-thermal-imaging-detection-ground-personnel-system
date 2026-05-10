import torch
import torch.nn as nn
import torch.nn.functional as F


class CARAFE(nn.Module):
    """Content-Aware ReAssembly of FEatures (CARAFE) upsampling module.

    Predicts per-pixel sampling offsets conditioned on local content, then
    applies bilinear grid-sampling to produce the upsampled feature map.
    This lightweight variant avoids the memory-heavy unfold operation of the
    original CARAFE, making it practical for high-resolution inputs.

    Reference:
        Wang et al., "CARAFE: Content-Aware ReAssembly of FEatures" (ICCV 2019)
        Liu et al., "Learning to Upsample by Learning to Sample" (ICCV 2023)
    """

    def __init__(self, c1, scale_factor=2, k_enc=3):
        """
        Args:
            c1: Input channels.
            scale_factor: Spatial upsampling factor (default: 2).
            k_enc: Encoder convolution kernel size (default: 3).
        """
        super().__init__()
        self.scale = scale_factor
        c_mid = max(c1 // 4, 16)

        self.encoder = nn.Sequential(
            nn.Conv2d(c1, c_mid, 1, bias=False),
            nn.BatchNorm2d(c_mid),
            nn.SiLU(),
            nn.Conv2d(c_mid, 2 * scale_factor ** 2, k_enc,
                      padding=k_enc // 2, bias=False),
        )
        # Small initial offsets → starts close to nearest-neighbour upsample
        nn.init.normal_(self.encoder[-1].weight, 0, 0.001)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, c, h, w = x.shape
        s = self.scale
        h_up, w_up = h * s, w * s

        # --- predict per-pixel sampling offsets ---
        offset = self.encoder(x)                        # (b, 2*s^2, h, w)
        offset = F.pixel_shuffle(offset, s)             # (b, 2, h_up, w_up)

        # --- build sampling grid ---
        grid_y, grid_x = torch.meshgrid(
            torch.arange(h_up, device=x.device, dtype=x.dtype),
            torch.arange(w_up, device=x.device, dtype=x.dtype),
            indexing="ij",
        )
        # Map each upsampled pixel back to its source coordinate + offset
        src_x = (grid_x + 0.5) / s - 0.5 + offset[:, 0]
        src_y = (grid_y + 0.5) / s - 0.5 + offset[:, 1]

        # Normalise to [-1, 1] for grid_sample
        src_x = 2.0 * src_x / max(w - 1, 1) - 1.0
        src_y = 2.0 * src_y / max(h - 1, 1) - 1.0
        grid = torch.stack([src_x, src_y], dim=-1)      # (b, h_up, w_up, 2)

        return F.grid_sample(
            x, grid, mode="bilinear", padding_mode="border", align_corners=True,
        )
