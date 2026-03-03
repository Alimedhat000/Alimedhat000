"""Convert an image file to ASCII art and write it to data/output.txt.

Run from the repo root:
    python scripts/convert_image.py
"""

import sys
import os

# Ensure repo root is on the path when this script is run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.image_to_ascii import image_to_ascii

ascii_art = image_to_ascii(
    "image.png", size=(80, 34), sharpness=3, brightness=1.5, scale=(0.5, 1.0)
)
print(ascii_art)

os.makedirs("data", exist_ok=True)
with open("data/output.txt", "w") as f:
    f.write(ascii_art)
