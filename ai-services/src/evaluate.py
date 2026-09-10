"""
evaluate.py
"""

import torch
from tqdm import tqdm
from dataset import get_dataloaders
from model import get_model
# ---- CONFIG ----
CHECKPOINT_PATH = "outputs/checkpoints/best_model.pth"  # match train.py's path
THRESHOLD = 0.5   # sigmoid output above this = predicted oil pixel


def compute_metrics(preds, targets, threshold=THRESHOLD, eps=1e-7):
    preds = (torch.sigmoid(preds) > threshold).float()
    targets = targets.float()

    preds_flat = preds.view(-1)
    targets_flat = targets.view(-1)

    tp = (preds_flat * targets_flat).sum()
    fp = (preds_flat * (1 - targets_flat)).sum()
    fn = ((1 - preds_flat) * targets_flat).sum()
    tn = ((1 - preds_flat) * (1 - targets_flat)).sum()

    iou = tp / (tp + fp + fn + eps)
    dice = (2 * tp) / (2 * tp + fp + fn + eps)
    precision = tp / (tp + fp + eps)
    recall = tp / (tp + fn + eps)

    return {
        "iou": iou.item(),
        "dice": dice.item(),
        "precision": precision.item(),
        "recall": recall.item(),
    }


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    print("Loading test data...")
    _, test_loader = get_dataloaders(
    processed_root="data/processed",
    batch_size=8
)


    print("Loading model...")
    model = get_model().to(device)
    model.load_state_dict(torch.load(CHECKPOINT_PATH, map_location=device))
    model.eval()

    totals = {"iou": 0.0, "dice": 0.0, "precision": 0.0, "recall": 0.0}
    n_batches = 0

    with torch.no_grad():
        for images, masks in tqdm(test_loader, desc="Evaluating"):
            images, masks = images.to(device), masks.to(device)
            outputs = model(images)

            batch_metrics = compute_metrics(outputs, masks)
            for k in totals:
                totals[k] += batch_metrics[k]
            n_batches += 1

    print("\n=== Test Set Metrics ===")
    for k in totals:
        avg = totals[k] / n_batches
        print(f"{k.capitalize():10s}: {avg:.4f}")


if __name__ == "__main__":
    main()
