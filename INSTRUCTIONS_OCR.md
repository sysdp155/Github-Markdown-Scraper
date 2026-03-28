# Image to Word Converter

This tool extracts text from images (like your dictionary page) and converts it to a Word document.

## Installation Steps

### 1. Install Python Dependencies
```bash
pip install -r requirements_ocr.txt
```

### 2. Install Tesseract OCR

**For Windows:**
1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (tesseract-ocr-w64-setup-5.3.3.exe or latest)
3. During installation, note the installation path (usually `C:\Program Files\Tesseract-OCR`)
4. Add Tesseract to your PATH or update the script with the path

**For other systems:**
- Mac: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

## Usage

### Method 1: Using the Script Directly

```python
from image_to_word import ImageToWordConverter

# Create converter
converter = ImageToWordConverter()

# If Tesseract is not in PATH, specify the path:
# converter = ImageToWordConverter(tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe')

# Convert your image
converter.convert_image_to_word('your_image.png', 'output.docx')
```

### Method 2: Command Line

Save your dictionary image as `dictionary.png` in the same folder, then run:

```bash
python image_to_word.py
```

## Notes

- Supports common image formats: PNG, JPG, JPEG, BMP, TIFF
- OCR accuracy depends on image quality
- For best results, use high-resolution, clear images
- The dictionary image you showed will be converted to a Word document with all the text extracted
