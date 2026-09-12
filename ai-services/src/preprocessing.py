"""
preprocessing.py
Converts raw Sentinel SAR images + RGB binary masks into
normalized, ready-to-train numpy arrays.

Expected input layout:
data/raw/archive/dataset/train/sentinel/image/0.png, 1.png, ...
data/raw/archive/dataset/train/sentinel/label/0.png, 1.png, ...
data/raw/archive/dataset/test/sentinel/image/...
data/raw/archive/dataset/test/sentinel/label/...

Output:
data/processed/train/images.npy   (N, 256, 256, 3) float32, values 0-1
data/processed/train/masks.npy    (N, 256, 256)    uint8, values 0 or 1
data/processed/test/images.npy
data/processed/test/masks.npy
"""

import os
import numpy as np
from PIL import Image
from tqdm import tqdm

# ---- CONFIG ----
RAW_ROOT = "data/raw/archive/dataset"
OUT_ROOT = "data/processed"
SENSOR = "sentinel"          # using sentinel only for the prototype
IMG_SIZE = 256                # dataset is already 256x256, kept for clarity/future resize


def load_image(path):
    img = Image.open(path).convert("RGB")
    if img.size != (IMG_SIZE, IMG_SIZE):
        img = img.resize((IMG_SIZE, IMG_SIZE))
    arr = np.array(img).astype(np.float32) / 255.0   # normalize to 0-1
    return arr


def load_mask(path):
    mask = Image.open(path).convert("RGB")
    if mask.size != (IMG_SIZE, IMG_SIZE):
        mask = mask.resize((IMG_SIZE, IMG_SIZE), resample=Image.NEAREST)
    arr = np.array(mask)
    # white [255,255,255] -> 1 (oil), black [0,0,0] -> 0 (background)
    binary_mask = (arr.sum(axis=-1) > 0).astype(np.uint8)
    return binary_mask


def process_split(split):
    """split = 'train' or 'test'"""
    img_dir = os.path.join(RAW_ROOT, split, SENSOR, "image")
    label_dir = os.path.join(RAW_ROOT, split, SENSOR, "label")

    filenames = sorted(
        [f for f in os.listdir(img_dir) if f.lower().endswith(".png")],
        key=lambda x: int(os.path.splitext(x)[0])
    )

    images = []
    masks = []
    skipped = []

    for fname in tqdm(filenames, desc=f"Processing {split}"):
        img_path = os.path.join(img_dir, fname)
        mask_path = os.path.join(label_dir, fname)

        if not os.path.exists(mask_path):
            skipped.append(fname)
            continue

        images.append(load_image(img_path))
        masks.append(load_mask(mask_path))

    images = np.stack(images)
    masks = np.stack(masks)

    out_dir = os.path.join(OUT_ROOT, split)
    os.makedirs(out_dir, exist_ok=True)
    np.save(os.path.join(out_dir, "images.npy"), images)
    np.save(os.path.join(out_dir, "masks.npy"), masks)

    print(f"\n{split.upper()} done: {images.shape[0]} pairs saved to {out_dir}")
    print(f"  images.npy shape: {images.shape}")
    print(f"  masks.npy shape:  {masks.shape}")
    if skipped:
        print(f"  WARNING: {len(skipped)} images had no matching mask, skipped: {skipped[:5]}...")

    # quick sanity check on class balance
    oil_ratio = masks.mean()
    print(f"  Oil pixel ratio: {oil_ratio:.4f} ({oil_ratio*100:.2f}% of all pixels are oil)")


if __name__ == "__main__":
    process_split("train")
    process_split("test")
    print("\nAll done. Check data/processed/train and data/processed/test")
