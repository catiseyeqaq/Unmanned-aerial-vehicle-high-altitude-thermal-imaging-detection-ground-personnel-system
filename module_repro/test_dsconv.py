import torch
from ultralytics.nn.Attention import DSConv

def main():
    x = torch.randn(2, 64, 80, 80)
    m = DSConv(64, 128, 9)
    y = m(x)
    print('ok', y.shape)

if __name__ == '__main__':
    main()
