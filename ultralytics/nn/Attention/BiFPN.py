import torch
import torch.nn as nn
import torch.nn.functional as F


class _BiFPNAdd(nn.Module):
    """BiFPN-style weighted feature fusion with normalized non-negative weights."""

    n_inputs = 0

    def __init__(self, eps=1e-4):
        super().__init__()
        self.eps = float(eps)
        self.w = nn.Parameter(torch.ones(self.n_inputs, dtype=torch.float32), requires_grad=True)

    def forward(self, xs):
        if len(xs) != self.n_inputs:
            raise ValueError(f"{self.__class__.__name__} expects {self.n_inputs} inputs, but got {len(xs)}")
        weights = F.relu(self.w)
        weights = weights / (weights.sum() + self.eps)
        return sum(w * x for w, x in zip(weights, xs))


class BiFPNAdd2(_BiFPNAdd):
    """BiFPN weighted sum for two input features."""

    n_inputs = 2


class BiFPNAdd3(_BiFPNAdd):
    """BiFPN weighted sum for three input features."""

    n_inputs = 3
