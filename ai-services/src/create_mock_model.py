"""
create_mock_model.py
Creates a minimal trained model checkpoint for testing purposes.
Run this once before starting the API server if training data is not available.

Usage:
    python src/create_mock_model.py
"""

import os
import torch
from pathlib import Path
from model import get_model

CHECKPOINT_DIR = "outputs/checkpoints"
BEST_MODEL_PATH = os.path.join(CHECKPOINT_DIR, "best_model.pth")


def create_mock_model():
    """Create and save a minimal model checkpoint for testing."""
    print("Creating mock model checkpoint for testing...")
    
    # Create output directory
    Path(CHECKPOINT_DIR).mkdir(parents=True, exist_ok=True)
    
    # Initialize the model
    model = get_model()
    
    # Save the initial state (untrained, but valid)
    torch.save(model.state_dict(), BEST_MODEL_PATH)
    
    print(f"✓ Mock model checkpoint created at: {BEST_MODEL_PATH}")
    print(f"  File size: {os.path.getsize(BEST_MODEL_PATH) / (1024*1024):.2f} MB")
    print("\nNote: This is an untrained model for testing purposes only.")
    print("For production, run: python src/train.py with proper training data.")


if __name__ == "__main__":
    create_mock_model()
