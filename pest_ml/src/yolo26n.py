import torch
import torch.nn as nn
from .head import M3DetectHead

class ConvModule(nn.Module):
    def __init__(self, c1, c2, k=1, s=1, p=None, g=1, act=True):
        super().__init__()
        p = p if p is not None else k // 2
        self.conv = nn.Conv2d(c1, c2, k, s, p, groups=g, bias=False)
        self.bn = nn.BatchNorm2d(c2)
        self.act = nn.SiLU() if act else nn.Identity()

    def forward(self, x):
        return self.act(self.bn(self.conv(x)))

class Bottleneck(nn.Module):
    def __init__(self, c1, c2, shortcut=True, g=1, e=0.5):
        super().__init__()
        c_ = int(c2 * e)
        self.cv1 = ConvModule(c1, c_, 1, 1)
        self.cv2 = ConvModule(c_, c2, 3, 1, g=g)
        self.add = shortcut and c1 == c2

    def forward(self, x):
        return x + self.cv2(self.cv1(x)) if self.add else self.cv2(self.cv1(x))

class C2f(nn.Module):
    def __init__(self, c1, c2, n=1, shortcut=False, g=1, e=0.5):
        super().__init__()
        self.c = int(c2 * e)
        self.cv1 = ConvModule(c1, 2 * self.c, 1, 1)
        self.cv2 = ConvModule((2 + n) * self.c, c2, 1)
        self.m = nn.ModuleList(Bottleneck(self.c, self.c, shortcut, g, e=1.0) for _ in range(n))

    def forward(self, x):
        y = list(self.cv1(x).chunk(2, 1))
        y.extend(m(y[-1]) for m in self.m)
        return self.cv2(torch.cat(y, 1))

class SPPF(nn.Module):
    def __init__(self, c1, c2, k=5):
        super().__init__()
        c_ = c1 // 2
        self.cv1 = ConvModule(c1, c_, 1, 1)
        self.cv2 = ConvModule(c_ * 4, c2, 1, 1)
        self.m = nn.MaxPool2d(kernel_size=k, stride=1, padding=k // 2)

    def forward(self, x):
        x = self.cv1(x)
        y1 = self.m(x)
        y2 = self.m(y1)
        return self.cv2(torch.cat((x, y1, y2, self.m(y2)), 1))

class YOLO26n(nn.Module):
    """YOLO26n baseline detector."""
    def __init__(self, num_classes=24):
        super().__init__()
        self.num_classes = num_classes
        
        # Backbone (P3, P4, P5)
        self.stem = ConvModule(3, 16, 3, 2)
        self.layer1 = nn.Sequential(ConvModule(16, 32, 3, 2), C2f(32, 32, 1, True))
        self.layer2 = nn.Sequential(ConvModule(32, 64, 3, 2), C2f(64, 64, 2, True)) # P3
        self.layer3 = nn.Sequential(ConvModule(64, 128, 3, 2), C2f(128, 128, 2, True)) # P4
        self.layer4 = nn.Sequential(ConvModule(128, 256, 3, 2), C2f(256, 256, 1, True), SPPF(256, 256)) # P5
        
        # PAN Neck
        self.up1 = nn.Upsample(scale_factor=2, mode='nearest')
        self.cv_p4 = ConvModule(256, 128, 1, 1)
        self.p4_p3 = C2f(256, 128, 1, False)
        
        self.up2 = nn.Upsample(scale_factor=2, mode='nearest')
        self.cv_p3 = ConvModule(128, 64, 1, 1)
        self.p3_p2 = C2f(128, 64, 1, False)
        
        self.down1 = ConvModule(64, 64, 3, 2)
        self.p3_p4_out = C2f(192, 128, 1, False)
        
        self.down2 = ConvModule(128, 128, 3, 2)
        self.p4_p5_out = C2f(384, 256, 1, False)
        
        # Head (reusing M3DetectHead but mapped to PAN outputs)
        self.head = M3DetectHead(num_classes, (64, 128, 256))

    def forward(self, x):
        x = self.stem(x)
        x = self.layer1(x)
        p3 = self.layer2(x)
        p4 = self.layer3(p3)
        p5 = self.layer4(p4)
        
        # Top down
        feat_p4 = self.p4_p3(torch.cat([self.up1(self.cv_p4(p5)), p4], 1))
        feat_p3 = self.p3_p2(torch.cat([self.up2(self.cv_p3(feat_p4)), p3], 1))
        
        # Bottom up
        feat_p4_out = self.p3_p4_out(torch.cat([self.down1(feat_p3), feat_p4], 1))
        feat_p5_out = self.p4_p5_out(torch.cat([self.down2(feat_p4_out), p5], 1))
        
        return self.head([feat_p3, feat_p4_out, feat_p5_out])
