import torch
import timm


def main():
    print("PyTorch:", torch.__version__)

    device = (
        "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )

    print("Device:", device)

    model = timm.create_model(
        "mobilenetv4_conv_small.e2400_r224_in1k",
        pretrained=True,
        num_classes=1000,
    )

    model.eval().to(device)

    x = torch.randn(
        1, 3, 256, 256,
        device=device
    )

    with torch.no_grad():
        y = model(x)

    params = sum(
        p.numel()
        for p in model.parameters()
    )

    print("Input :", tuple(x.shape))
    print("Output:", tuple(y.shape))
    print(f"Params: {params:,}")


if __name__ == "__main__":
    main()