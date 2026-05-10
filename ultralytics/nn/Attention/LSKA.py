import torch.nn as nn


class LSKA(nn.Module):
    def __init__(self, c1, c2, k=11, act=True):
        super().__init__()
        self.norm = nn.BatchNorm2d(c1)
        self.pw1 = nn.Conv2d(c1, c1, 1, 1, 0, bias=False)

        self.dw_h1 = nn.Conv2d(c1, c1, kernel_size=(1, 5), stride=1, padding=(0, 2), groups=c1, bias=False)
        self.dw_v1 = nn.Conv2d(c1, c1, kernel_size=(5, 1), stride=1, padding=(2, 0), groups=c1, bias=False)

        if k <= 7:
            k2 = 7
            d = 2
        elif k <= 11:
            k2 = 9
            d = 2
        elif k <= 23:
            k2 = 13
            d = 3
        else:
            k2 = 17
            d = 3

        p2 = ((k2 - 1) // 2) * d
        self.dw_h2 = nn.Conv2d(
            c1, c1, kernel_size=(1, k2), stride=1, padding=(0, p2), dilation=(1, d), groups=c1, bias=False
        )
        self.dw_v2 = nn.Conv2d(
            c1, c1, kernel_size=(k2, 1), stride=1, padding=(p2, 0), dilation=(d, 1), groups=c1, bias=False
        )

        self.pw2 = nn.Conv2d(c1, c1, 1, 1, 0, bias=False)
        self.act = nn.SiLU() if act else nn.Identity()

        self.proj = nn.Conv2d(c1, c2, 1, 1, 0, bias=False) if c1 != c2 else nn.Identity()
        self.out_bn = nn.BatchNorm2d(c2)
        self.out_act = nn.SiLU()

    def forward(self, x):
        u = x
        x = self.norm(x)
        x = self.pw1(x)
        x = self.dw_h1(x)
        x = self.dw_v1(x)
        x = self.dw_h2(x)
        x = self.dw_v2(x)
        x = self.pw2(x)
        x = self.act(x)
        x = x * u
        x = self.proj(x)
        x = self.out_bn(x)
        x = self.out_act(x)
        return x
