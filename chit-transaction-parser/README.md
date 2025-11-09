# Transaction Parser

An automated Python script that extracts transaction data from payment receipt images and generates a structured CSV file with totals.

## What This Script Does

This script automatically:
1. **Reads** all transaction receipt images from the `transactions/` folder
2. **Extracts** text from images using OCR (Optical Character Recognition)
3. **Parses** the following information from each receipt:
   - Transaction Date (formatted as DD-MMM-YY, e.g., 04-Jan-25)
   - Amount Transferred (e.g., 25200)
   - Transaction ID (e.g., T2501045645339710326890)
4. **Adds** a static "Chit Amount" field (40,000) to each transaction
5. **Generates** a CSV file (`transactions.csv`) with all extracted data
6. **Calculates** and appends totals at the end:
   - Total Amount Transferred across all transactions
   - Total Chit Amount (number of transactions × 40,000)

### Example Output

The generated CSV looks like this:

```
Transaction Date,Amount Transferred,Transaction ID,Chit Amount,Source File
04-Jan-25,25200,T2501046745339710326890,40000,WhatsApp Image 2025-01-04 at 20.45.57.jpeg
02-Feb-25,30600,T2502027824222478708532,40000,WhatsApp Image 2025-02-02 at 15.24.48.jpeg
...
TOTAL,372960.00,,440000,
```

---

## Complete Setup Guide

### Step 1: Install Python

**For Windows:**
1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **IMPORTANT:** Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Verify installation: Open Command Prompt and type:
   ```
   python --version
   ```

**For macOS:**
1. Install Homebrew (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```bash
   brew install python
   ```
3. Verify installation:
   ```bash
   python3 --version
   ```

**For Ubuntu/Linux:**
1. Update package list:
   ```bash
   sudo apt update
   ```
2. Install Python and pip:
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```
3. Verify installation:
   ```bash
   python3 --version
   ```

---

### Step 2: Install Tesseract OCR

Tesseract is the OCR engine that reads text from images.

**For Windows:**
1. Download the installer from: [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the `.exe` file
3. During installation:
   - Use default path: `C:\Program Files\Tesseract-OCR`
   - Select "Install all language files" or at least English
4. Complete the installation
5. The script is already configured to find Tesseract at this default location

**For macOS:**
```bash
brew install tesseract
```

**For Ubuntu/Linux:**
```bash
sudo apt install tesseract-ocr
```

---

### Step 3: Set Up the Project

**For Windows (PowerShell or Command Prompt):**

1. Open PowerShell or Command Prompt
2. Navigate to the project folder:
   ```powershell
   cd "path\to\chits"
   ```
3. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
4. Activate the virtual environment:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   If you get an error about execution policies, run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
   Then try activating again.

5. Install required packages:
   ```powershell
   pip install pillow pytesseract pandas
   ```

**For macOS/Linux (Terminal):**

1. Open Terminal
2. Navigate to the project folder:
   ```bash
   cd /path/to/chits
   ```
3. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```
4. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
5. Install required packages:
   ```bash
   pip install pillow pytesseract pandas
   ```

---

## How to Use

### Running the Script

**Windows (with virtual environment activated):**
```powershell
python parse_transactions.py
```

**Windows (without activating virtual environment):**
```powershell
.venv\Scripts\python.exe parse_transactions.py
```

**macOS/Linux (with virtual environment activated):**
```bash
python parse_transactions.py
```

**macOS/Linux (without activating virtual environment):**
```bash
.venv/bin/python parse_transactions.py
```

### Workflow

1. **Place your transaction images** in the `transactions/` folder
   - Supported formats: `.jpg`, `.jpeg`, `.png`, `.bmp`
   - Any number of images is supported

2. **Run the script** using one of the commands above

3. **Check the output**:
   - The script will show progress as it processes each image
   - A summary will be displayed at the end
   - `transactions.csv` will be created/updated in the same folder

4. **Open the CSV file**:
   - Open with Excel, Google Sheets, or any spreadsheet application
   - Verify the extracted data
   - Make any manual corrections if needed

### Example Output

When you run the script, you'll see:

```
============================================================
Transaction Parser - Extracting data from images...
============================================================
Found 11 images to process...
Processing: WhatsApp Image 2025-01-04 at 20.45.57.jpeg
Processing: WhatsApp Image 2025-02-02 at 15.24.48.jpeg
...

✓ CSV file generated: transactions.csv
  Total transactions: 11
  Total Chit Amount: ₹440,000
  Total Amount Transferred: ₹372,960.00
```

---

## File Structure

```
chits/
├── transactions/              # Folder containing transaction images
│   ├── WhatsApp Image 2025-01-04 at 20.45.57.jpeg
│   ├── WhatsApp Image 2025-02-02 at 15.24.48.jpeg
│   └── ...
├── parse_transactions.py      # Main script
├── debug_ocr.py              # Debug tool (optional)
├── transactions.csv          # Generated output (created after running script)
├── README.md                 # This file
└── .venv/                    # Virtual environment (created during setup)
```

---

## Troubleshooting

### "tesseract is not installed or it's not in your PATH"

**Windows:**
- Make sure Tesseract is installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`
- If installed elsewhere, update line 18 in `parse_transactions.py`:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r'C:\Your\Custom\Path\tesseract.exe'
  ```

**macOS/Linux:**
- Verify Tesseract is installed:
  ```bash
  which tesseract
  ```
- If installed, comment out line 18 in `parse_transactions.py` (it should auto-detect)

### "python is not recognized as a command"

- Python is not in your PATH
- **Windows:** Reinstall Python and check "Add Python to PATH"
- **macOS/Linux:** Use `python3` instead of `python`

### Poor or Incorrect Data Extraction

- Ensure images are clear and high resolution
- Check that text in images is not blurry or distorted
- Manually verify/correct the CSV after generation
- Use `debug_ocr.py` to see what text is being extracted:
  ```bash
  python debug_ocr.py
  ```

### Permission Errors (macOS/Linux)

If you get permission errors, use:
```bash
chmod +x parse_transactions.py
```

---

## Advanced Configuration

### Changing the Chit Amount

Edit line 20 in `parse_transactions.py`:
```python
CHIT_AMOUNT = 40000  # Change this value
```

### Changing Date Format

Edit the `normalize_date()` function (around line 30):
```python
return parsed_date.strftime('%d-%b-%y')  # Current: DD-MMM-YY (e.g., 04-Jan-25)
# return parsed_date.strftime('%Y-%m-%d')  # Alternative: YYYY-MM-DD (e.g., 2025-01-04)
# return parsed_date.strftime('%m/%d/%Y')  # Alternative: MM/DD/YYYY (e.g., 01/04/2025)
```

### Processing Specific Images Only

You can temporarily move images out of the `transactions/` folder to process only certain ones.

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify all prerequisites are installed correctly
3. Run `debug_ocr.py` to see what text is being extracted from images
4. Manually review the generated CSV and correct any errors

---

## Technical Details

**Dependencies:**
- `Pillow` (PIL) - Image processing
- `pytesseract` - Python wrapper for Tesseract OCR
- `pandas` - Data manipulation and CSV generation
- `Tesseract OCR` - OCR engine (system-level installation)

**Python Version:** 3.7 or higher recommended

**Supported Image Formats:** JPEG, PNG, BMP

**OCR Language:** English (default)

---

## License

This script is provided as-is for personal use.

