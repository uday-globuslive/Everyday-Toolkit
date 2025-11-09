"""
Debug script to see what OCR is extracting from images
"""

from PIL import Image
import pytesseract
from pathlib import Path

# Configure pytesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def debug_image(image_path):
    """Extract and print text from a single image"""
    print(f"\n{'='*80}")
    print(f"File: {image_path.name}")
    print('='*80)
    
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    
    print(text)
    print('='*80)

# Test with the first image
trans_dir = Path(__file__).parent / 'transactions'
images = sorted([f for f in trans_dir.iterdir() if f.suffix.lower() in ['.jpg', '.jpeg', '.png']])

# Test with the last 3 images to check October and November
for img in images[-3:]:
    debug_image(img)
