import torch

from ultralytics.nn.Attention import LSKA


def main():
    x = torch.randn(2, 64, 80, 80)
    m = LSKA(64, 128, 11)
    y = m(x)
    print("ok", y.shape)


if __name__ == "__main__":
    main()
