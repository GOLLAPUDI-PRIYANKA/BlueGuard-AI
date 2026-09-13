"""
model.py
"""

import torch
import segmentation_models_pytorch as smp


def get_model():
    model = smp.Unet(
        encoder_name="resnet34",        # pretrained encoder backbone
        encoder_weights="imagenet",     # use ImageNet pretrained weights
        in_channels=3,                  # RGB input
        classes=1,                      # binary segmentation: oil vs not-oil
        activation=None,                # we apply sigmoid manually (raw logits out)
    )
    return model


if __name__ == "__main__":
    # quick sanity check: does a forward pass work end-to-end?
    model = get_model()
    dummy_input = torch.randn(2, 3, 256, 256)   # batch of 2 fake images
    output = model(dummy_input)
    print("Input shape: ", dummy_input.shape)
    print("Output shape:", output.shape)         # expect (2, 1, 256, 256)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total params: {total_params:,}")
    print(f"Trainable params: {trainable_params:,}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device available: {device}")