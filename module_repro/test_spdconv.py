import torch

from ultralytics.nn.Attention import SPDConv


def main():
    x = torch.randn(2, 64, 80, 80)
    m = SPDConv(64, 64)
    y = m(x)
    print("ok", y.shape)


if __name__ == "__main__":
    main()
