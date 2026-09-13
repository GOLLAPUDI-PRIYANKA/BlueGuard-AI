"""
train.py (v2)
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm

from dataset import get_dataloaders
from model import get_model

# ---- CONFIG ----
EPOCHS = 50
BATCH_SIZE = 8
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-5
CHECKPOINT_DIR = "outputs/checkpoints"   # adjust if needed
BEST_MODEL_PATH = os.path.join(CHECKPOINT_DIR, "best_model.pth")


def dice_loss(preds, targets, smooth=1.0):
    preds = torch.sigmoid(preds)
    preds = preds.view(-1)
    targets = targets.view(-1)
    intersection = (preds * targets).sum()
    dice = (2. * intersection + smooth) / (preds.sum() + targets.sum() + smooth)
    return 1 - dice


def combo_loss(preds, targets):
    bce = nn.functional.binary_cross_entropy_with_logits(preds, targets)
    dice = dice_loss(preds, targets)
    return bce + dice


def train_one_epoch(model, loader, optimizer, device):
    model.train()
    running_loss = 0.0
    for images, masks in tqdm(loader, desc="Training", leave=False):
        images, masks = images.to(device), masks.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = combo_loss(outputs, masks)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * images.size(0)
    return running_loss / len(loader.dataset)


def validate(model, loader, device):
    model.eval()
    running_loss = 0.0
    with torch.no_grad():
        for images, masks in tqdm(loader, desc="Validating", leave=False):
            images, masks = images.to(device), masks.to(device)
            outputs = model(images)
            loss = combo_loss(outputs, masks)
            running_loss += loss.item() * images.size(0)
    return running_loss / len(loader.dataset)


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    print("Loading data...")
    train_loader, val_loader = get_dataloaders(processed_root="data/processed", batch_size=BATCH_SIZE)
    print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")

    print("Building fresh model...")
    model = get_model().to(device)   # fresh model, not loading old weights
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=3
    )

    best_val_loss = float("inf")

    for epoch in range(1, EPOCHS + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, device)
        val_loss = validate(model, val_loader, device)
        scheduler.step(val_loss)

        current_lr = optimizer.param_groups[0]["lr"]
        print(f"Epoch {epoch}/{EPOCHS} - train_loss: {train_loss:.4f} - val_loss: {val_loss:.4f} - lr: {current_lr:.6f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), BEST_MODEL_PATH)
            print(f"  -> New best model saved (val_loss: {val_loss:.4f})")

    print("\nTraining complete.")
    print(f"Best val_loss: {best_val_loss:.4f}")
    print(f"Best model saved at: {BEST_MODEL_PATH}")


if __name__ == "__main__":
    main()