"""
dataset.py
"""

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader


class OilSpillDataset(Dataset):
    def __init__(self, images_path, masks_path, augment=False):
        self.images = np.load(images_path)   # (N, 256, 256, 3) float32, 0-1
        self.masks = np.load(masks_path)     # (N, 256, 256) uint8, 0/1
        self.augment = augment

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image = self.images[idx].copy()   # (H, W, 3)
        mask = self.masks[idx].copy()     # (H, W)

        if self.augment:
            # random horizontal flip
            if np.random.rand() > 0.5:
                image = np.fliplr(image).copy()
                mask = np.fliplr(mask).copy()
            # random vertical flip
            if np.random.rand() > 0.5:
                image = np.flipud(image).copy()
                mask = np.flipud(mask).copy()
            # random 90-degree rotation
            k = np.random.randint(0, 4)
            image = np.rot90(image, k).copy()
            mask = np.rot90(mask, k).copy()

        # convert to torch tensors, channel-first for images: (3, H, W)
        image_tensor = torch.from_numpy(image).permute(2, 0, 1).float()
        mask_tensor = torch.from_numpy(mask).unsqueeze(0).float()  # (1, H, W)

        return image_tensor, mask_tensor


def get_dataloaders(processed_root="data/processed", batch_size=8, num_workers=0):
    train_ds = OilSpillDataset(
        images_path=f"{processed_root}/train/images.npy",
        masks_path=f"{processed_root}/train/masks.npy",
        augment=True,
    )
    test_ds = OilSpillDataset(
        images_path=f"{processed_root}/test/images.npy",
        masks_path=f"{processed_root}/test/masks.npy",
        augment=False,
    )

    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, drop_last=True
    )
    test_loader = DataLoader(
        test_ds, batch_size=batch_size, shuffle=False,
        num_workers=num_workers
    )

    return train_loader, test_loader


if __name__ == "__main__":
    # quick sanity check
    train_loader, test_loader = get_dataloaders(batch_size=4)
    images, masks = next(iter(train_loader))
    print("Batch images shape:", images.shape)   # expect (4, 3, 256, 256)
    print("Batch masks shape: ", masks.shape)    # expect (4, 1, 256, 256)
    print("Image value range:", images.min().item(), "-", images.max().item())
    print("Mask unique values:", torch.unique(masks))
    print(f"Train batches per epoch: {len(train_loader)}")
    print(f"Test batches: {len(test_loader)}")
