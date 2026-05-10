import torch
import torch.nn as nn


class SimAM(nn.Module):
    """SimAM: A Simple, Parameter-Free Attention Module for CNNs.

    Computes 3D attention weights based on energy theory without any learnable
    parameters.  Each neuron gets a unique importance weight derived from the
    difference between itself and the local mean, providing both channel and spatial awareness at zero parameter cost.

    References:
        Yang et al., "SimAM: A Simple, Parameter-Free Attention Module for
        Convolutional Neural Networks" (ICML 2021)
    """

    def __init__(self, c1=None, e_lambda=1e-4):
        """
        Args:
            c1: Input channels (accepted for YOLO parser compatibility, not used).
            e_lambda: Regularization coefficient to avoid division by zero.
        """
        super().__init__()
        self.e_lambda = e_lambda

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _b, _c, h, w = x.size()
        n = h * w - 1
        # Per-neuron energy: how different each value is from its spatial mean
        x_minus_mu_sq = (x - x.mean(dim=[2, 3], keepdim=True)).pow(2)
        y = x_minus_mu_sq / (4 * (x_minus_mu_sq.sum(dim=[2, 3], keepdim=True) / n + self.e_lambda)) + 0.5
        return x * y.sigmoid()
