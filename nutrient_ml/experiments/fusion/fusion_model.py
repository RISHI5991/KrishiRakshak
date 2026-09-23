import torch
import torch.nn as nn


# =========================================================
# DHURANDHAR - MULTIMODAL NPK FUSION MODEL
# =========================================================

NUM_IMAGE_FEATURES = 1280
NUM_SENSOR_FEATURES = 5

IMAGE_EMBEDDING_SIZE = 128
SENSOR_EMBEDDING_SIZE = 32

NUM_CLASSES = 4

CLASS_NAMES = [
    "Healthy",
    "K_Deficiency",
    "N_Deficiency",
    "P_Deficiency",
]


# =========================================================
# IMAGE ENCODER
# =========================================================

class ImageEncoder(nn.Module):

    def __init__(self):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(
                NUM_IMAGE_FEATURES,
                512
            ),
            nn.ReLU(),
            nn.Dropout(0.20),

            nn.Linear(
                512,
                IMAGE_EMBEDDING_SIZE
            ),
            nn.ReLU(),
        )

    def forward(self, x):
        return self.network(x)


# =========================================================
# SENSOR ENCODER
# =========================================================

class SensorEncoder(nn.Module):

    def __init__(self):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(
                NUM_SENSOR_FEATURES,
                32
            ),
            nn.ReLU(),

            nn.Linear(
                32,
                SENSOR_EMBEDDING_SIZE
            ),
            nn.ReLU(),
        )

    def forward(self, x):
        return self.network(x)


# =========================================================
# FUSION MODEL
# =========================================================

class NPKFusionModel(nn.Module):

    def __init__(self):
        super().__init__()

        self.image_encoder = ImageEncoder()

        self.sensor_encoder = SensorEncoder()

        self.classifier = nn.Sequential(

            nn.Linear(
                IMAGE_EMBEDDING_SIZE
                + SENSOR_EMBEDDING_SIZE,
                64
            ),

            nn.ReLU(),

            nn.Dropout(0.20),

            nn.Linear(
                64,
                NUM_CLASSES
            ),
        )

    def forward(
        self,
        image_features,
        sensor_features,
    ):

        image_embedding = self.image_encoder(
            image_features
        )

        sensor_embedding = self.sensor_encoder(
            sensor_features
        )

        combined = torch.cat(
            [
                image_embedding,
                sensor_embedding,
            ],
            dim=1,
        )

        logits = self.classifier(
            combined
        )

        return logits


# =========================================================
# MODEL TEST
# =========================================================

if __name__ == "__main__":

    print("======================================")
    print("DHURANDHAR NPK FUSION MODEL")
    print("======================================")

    model = NPKFusionModel()

    print()
    print("Model created successfully.")

    print()
    print("Image features :", NUM_IMAGE_FEATURES)
    print("Sensor features:", NUM_SENSOR_FEATURES)

    print()
    print("Image embedding :", IMAGE_EMBEDDING_SIZE)
    print("Sensor embedding:", SENSOR_EMBEDDING_SIZE)

    print()
    print("Classes:")
    for i, name in enumerate(CLASS_NAMES):
        print(f"  {i}: {name}")

    # -----------------------------------------------------
    # Dummy data ONLY for architecture testing.
    # This is NOT training data.
    # -----------------------------------------------------

    batch_size = 4

    dummy_image_features = torch.randn(
        batch_size,
        NUM_IMAGE_FEATURES
    )

    dummy_sensor_features = torch.randn(
        batch_size,
        NUM_SENSOR_FEATURES
    )

    output = model(
        dummy_image_features,
        dummy_sensor_features,
    )

    print()
    print("Input image shape  :",
          dummy_image_features.shape)

    print("Input sensor shape :",
          dummy_sensor_features.shape)

    print("Output shape       :",
          output.shape)

    print()
    print("Expected output:")
    print("(batch_size, 4)")

    print()
    print("======================================")
    print("FUSION MODEL TEST COMPLETE")
    print("======================================")