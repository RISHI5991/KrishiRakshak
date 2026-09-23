from pathlib import Path

import torch
import timm
import numpy as np

from PIL import Image
import matplotlib.pyplot as plt

from torchvision import transforms


# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = Path(r"D:\Dhurandhar\nutrient_ml\models\npk_vision_baseline_v1.pt")

DATA_DIR = Path(
    r"D:\Dhurandhar\nutrient_ml\data\HARN_Rice"
)

OUTPUT_DIR = Path(
    r"D:\Dhurandhar\nutrient_ml\experiments\baseline_v1\gradcam\outputs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MODEL_NAME = (
    "mobilenetv4_conv_small.e2400_r224_in1k"
)

CLASS_NAMES = [
    "Healthy",
    "K_Deficiency",
    "N_Deficiency",
    "P_Deficiency",
]

IMG_SIZE = 224

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading model...")

model = timm.create_model(
    MODEL_NAME,
    pretrained=False,
    num_classes=4,
)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE,
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(DEVICE)
model.eval()

print("Model loaded.")


# ============================================================
# FIND LAST CONVOLUTIONAL LAYER
# ============================================================

# ---------------------------------------------------------
# Find a convolution layer that still has spatial features
# ---------------------------------------------------------
target_layer = None

conv_layers = [
    module
    for module in model.modules()
    if isinstance(module, torch.nn.Conv2d)
]

if not conv_layers:
    raise RuntimeError("Could not find any Conv2d layer.")

# The final Conv2d in MobileNetV4 can occur after spatial
# information has already been collapsed. Try earlier layers.
with torch.no_grad():
    dummy = torch.zeros(
        1, 3, IMG_SIZE, IMG_SIZE,
        device=DEVICE
    )

    for module in reversed(conv_layers):
        captured = []

        def test_hook(m, inp, output):
            captured.append(output)

        handle = module.register_forward_hook(test_hook)

        try:
            model(dummy)
        finally:
            handle.remove()

        if captured:
            output_shape = captured[0].shape

            # We want [B, C, H, W] with H and W > 1
            if (
                len(output_shape) == 4
                and output_shape[2] > 1
                and output_shape[3] > 1
            ):
                target_layer = module
                break

if target_layer is None:
    raise RuntimeError(
        "Could not find a Conv2d layer with a spatial feature map."
    )

print("Grad-CAM target layer:", target_layer)


if target_layer is None:

    raise RuntimeError(
        "Could not find Conv2d layer."
    )


print(
    "Grad-CAM target layer:",
    target_layer
)


# ============================================================
# HOOKS
# ============================================================

activations = None
gradients = None


def forward_hook(
    module,
    input,
    output
):

    global activations

    activations = output.detach()


def backward_hook(
    module,
    grad_input,
    grad_output
):

    global gradients

    gradients = (
        grad_output[0]
        .detach()
    )


target_layer.register_forward_hook(
    forward_hook
)

target_layer.register_full_backward_hook(
    backward_hook
)


# ============================================================
# PREPROCESSING
# ============================================================

transform = transforms.Compose([

    transforms.Resize(
        (IMG_SIZE, IMG_SIZE)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225],
    ),
])


# ============================================================
# GRAD-CAM FUNCTION
# ============================================================

def generate_gradcam(
    image_path
):

    global activations
    global gradients

    activations = None
    gradients = None

    image = Image.open(
        image_path
    ).convert("RGB")

    original_image = image.copy()

    tensor = transform(
        image
    ).unsqueeze(0).to(DEVICE)

    # Forward pass
    output = model(tensor)

    probabilities = torch.softmax(
        output,
        dim=1
    )

    predicted_index = int(
        output.argmax(
            dim=1
        ).item()
    )

    predicted_probability = float(
        probabilities[
            0,
            predicted_index
        ].item()
    )

    # Clear previous gradients
    model.zero_grad()

    # Backpropagate predicted class
    score = output[
        0,
        predicted_index
    ]

    score.backward()

    # --------------------------------------------------------
    # Grad-CAM
    # --------------------------------------------------------

    weights = gradients.mean(
        dim=(2, 3),
        keepdim=True
    )

    cam = (
        weights * activations
    ).sum(
        dim=1
    )

    cam = torch.relu(
        cam
    )

    cam = cam.squeeze().cpu().numpy()

    if cam.ndim != 2:
        raise RuntimeError(
        f"Grad-CAM produced an invalid shape: {cam.shape}. "
        "The selected target layer does not contain a spatial feature map."
        )
    # Normalize
    cam -= cam.min()

    if cam.max() > 0:

        cam /= cam.max()

    cam_image = Image.fromarray(
        np.uint8(
            cam * 255
        )
    )

    cam_image = cam_image.resize(
        original_image.size,
        Image.Resampling.BILINEAR
    )

    cam_array = np.array(
        cam_image
    ) / 255.0

    # --------------------------------------------------------
    # Plot
    # --------------------------------------------------------

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(10, 5)
    )

    axes[0].imshow(
        original_image
    )

    axes[0].set_title(
        "Original"
    )

    axes[0].axis("off")


    axes[1].imshow(
        original_image
    )

    axes[1].imshow(
        cam_array,
        cmap="jet",
        alpha=0.45
    )

    axes[1].set_title(
        f"{CLASS_NAMES[predicted_index]}\n"
        f"Confidence: "
        f"{predicted_probability:.2%}"
    )

    axes[1].axis("off")


    plt.tight_layout()

    output_name = (
        Path(image_path).stem
        + "_gradcam.png"
    )

    output_path = (
        OUTPUT_DIR
        / output_name
    )

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()


    print(
        f"{Path(image_path).name}"
        f" → "
        f"{CLASS_NAMES[predicted_index]}"
        f" ({predicted_probability:.2%})"
    )

    return (
        predicted_index,
        predicted_probability,
        output_path
    )


# ============================================================
# SELECT EXAMPLES
# ============================================================

print("\nSelecting examples...")

selected_images = []

for class_name in CLASS_NAMES:

    class_dir = (
        DATA_DIR
        / class_name
    )

    images = list(
        class_dir.glob("*.jpg")
    )

    if len(images) == 0:

        images = list(
            class_dir.glob("*")
        )

    if images:

        selected_images.append(
            (
                class_name,
                images[0]
            )
        )


# ============================================================
# GENERATE CAM
# ============================================================

print("\nGenerating Grad-CAM...\n")

for class_name, image_path in selected_images:

    generate_gradcam(
        image_path
    )


print("\nDone.")

print(
    "Outputs saved to:"
)

print(OUTPUT_DIR)