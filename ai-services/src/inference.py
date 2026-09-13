"""
inference.py
Runs the trained model on a single input image and produces:
- a binary mask
- a confidence score
- polygon coordinates of detected oil spill regions (for GIS use)
"""

import numpy as np
import torch
import cv2
from PIL import Image
from model import get_model


CHECKPOINT_PATH = "outputs/checkpoints/best_model.pth"
IMG_SIZE = 256
THRESHOLD = 0.5

_device = "cuda" if torch.cuda.is_available() else "cpu"
_model = None


def load_model():
    global _model
    if _model is None:
        _model = get_model().to(_device)
        _model.load_state_dict(torch.load(CHECKPOINT_PATH, map_location=_device))
        _model.eval()
    return _model


def preprocess_image(image_path):
    img = Image.open(image_path).convert("RGB")
    if img.size != (IMG_SIZE, IMG_SIZE):
        img = img.resize((IMG_SIZE, IMG_SIZE))
    arr = np.array(img).astype(np.float32) / 255.0
    tensor = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).float()
    return tensor


def mask_to_polygons(binary_mask):
    """Convert a binary mask (H, W) of 0/1 into a list of polygons.
    Each polygon is a list of [x, y] points."""
    mask_uint8 = (binary_mask * 255).astype(np.uint8)
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    polygons = []
    for contour in contours:
        if cv2.contourArea(contour) < 10:   # skip tiny noise blobs
            continue
        polygon = contour.squeeze().tolist()
        if isinstance(polygon[0], int):     # single point edge case
            continue
        polygons.append(polygon)

    return polygons


def predict(image_path):
    """
    Main inference function.
    Returns a dict matching the team's API contract shape:
    { mask, confidence, polygons }
    """
    model = load_model()
    input_tensor = preprocess_image(image_path).to(_device)

    with torch.no_grad():
        output = model(input_tensor)
        prob_map = torch.sigmoid(output).squeeze().cpu().numpy()   # (H, W), values 0-1

    binary_mask = (prob_map > THRESHOLD).astype(np.uint8)
    confidence = float(prob_map[binary_mask == 1].mean()) if binary_mask.sum() > 0 else 0.0
    polygons = mask_to_polygons(binary_mask)

    return {
        "mask": binary_mask,          # numpy array, (256, 256), 0/1 -- caller saves/serves as needed
        "confidence": round(confidence, 4),
        "polygons": polygons,         # list of [[x,y], [x,y], ...] per detected region
        "num_regions": len(polygons),
    }


if __name__ == "__main__":
    import sys
    test_image = sys.argv[1] if len(sys.argv) > 1 else "data/processed/test_sample.png"
    result = predict(test_image)
    print(f"Confidence: {result['confidence']}")
    print(f"Number of oil spill regions detected: {result['num_regions']}")
    print(f"First polygon (if any): {result['polygons'][0][:5] if result['polygons'] else 'None'}")
