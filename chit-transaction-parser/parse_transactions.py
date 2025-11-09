"""
Transaction Parser - Extract transaction data from images and generate CSV
"""

import os
import re
import csv
from datetime import datetime
from pathlib import Path
try:
    from PIL import Image
    import pytesseract
    import pandas as pd
except ImportError:
    print("Required packages not installed. Please install them first.")
    print("Run: pip install pytesseract pillow pandas")
    exit(1)

# Configure pytesseract path for Windows
# Set the default installation path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

CHIT_AMOUNT = 40000  # Static chit amount


def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return ""


def normalize_date(date_str):
    """Normalize date to DD-MMM-YYYY format"""
    if not date_str:
        return ''
    
    # Replace "Sept" with "Sep" for proper parsing
    date_str = date_str.replace('Sept', 'Sep')
    
    # Try to parse different date formats
    date_formats = [
        '%Y-%m-%d',           # 2025-01-04
        '%d-%m-%Y',           # 04-01-2025
        '%d/%m/%Y',           # 04/01/2025
        '%d %b %Y',           # 04 Jan 2025 or 04 Sep 2025
        '%d %B %Y',           # 04 January 2025
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime('%d-%b-%y')  # Return in DD-MMM-YY format (e.g., 04-Jan-25)
        except ValueError:
            continue
    
    # If all parsing fails, return original
    return date_str


def parse_transaction_data(text, filename):
    """Parse transaction data from OCR text"""
    transaction = {
        'Transaction Date': '',
        'Amount Transferred': '',
        'Transaction ID': '',
        'Chit Amount': CHIT_AMOUNT
    }
    
    # Extract date patterns (various formats)
    date_patterns = [
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',  # DD-MM-YYYY or DD/MM/YYYY
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',    # YYYY-MM-DD
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{2,4})',  # DD Mon YYYY
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            raw_date = date_match.group(1)
            transaction['Transaction Date'] = normalize_date(raw_date)
            break
    
    # If no date found in text, try to extract from filename
    if not transaction['Transaction Date']:
        filename_date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        if filename_date_match:
            raw_date = filename_date_match.group(1)
            transaction['Transaction Date'] = normalize_date(raw_date)
    
    # Extract amount (looking for patterns like ₹25,200 or %25,200 from OCR)
    # OCR often converts ₹ to % or other symbols, or sometimes drops it
    amount_patterns = [
        r'[₹%Rs\.]+\s*(\d{1,3}(?:,\d{3})+)',  # Currency symbol followed by comma-formatted number
        r'Paid to.*?[₹%=]\s*(\d{1,3}(?:,\d{3})+)',  # After "Paid to" label with symbol
        r'Paid to.*?\n.*?\n.*?(\d{1,3}(?:,\d{3})+)',  # After "Paid to" without symbol (2-3 lines down)
        r'Debited.*?[₹%=]\s*(\d{1,3}(?:,\d{3})+)',  # After "Debited" label
        r'(?:Amount|Amt|Total)[:\s]*[₹%Rs\.]*\s*(\d{1,3}(?:,\d{3})+)',  # With amount labels
        r'[=]\s*(\d{1,3}(?:,\d{3})+)',  # Just = followed by number
    ]
    
    for pattern in amount_patterns:
        amount_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '')
            # Validate it's a reasonable amount (between 1000 and 100000)
            try:
                amount_val = float(amount_str)
                if 1000 <= amount_val <= 100000:
                    transaction['Amount Transferred'] = amount_str
                    break
            except ValueError:
                continue
    
    # Extract transaction ID (various patterns)
    txn_patterns = [
        r'(?:Transaction ID|Txn ID|UTR|Reference)[:\s]*([A-Z0-9]{10,})',  # With labels
        r'(?:UPI|IMPS|NEFT)[:\s]*([A-Z0-9]{10,})',  # Payment method IDs
        r'\b([A-Z0-9]{12,})\b',  # Alphanumeric codes (12+ chars)
    ]
    
    for pattern in txn_patterns:
        txn_match = re.search(pattern, text, re.IGNORECASE)
        if txn_match:
            transaction['Transaction ID'] = txn_match.group(1)
            break
    
    return transaction


def process_transactions(transactions_folder='transactions'):
    """Process all images in the transactions folder"""
    script_dir = Path(__file__).parent
    trans_dir = script_dir / transactions_folder
    
    if not trans_dir.exists():
        print(f"Error: Folder '{transactions_folder}' not found!")
        return []
    
    transactions = []
    image_files = sorted([f for f in trans_dir.iterdir() 
                         if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']])
    
    print(f"Found {len(image_files)} images to process...")
    
    for img_file in image_files:
        print(f"Processing: {img_file.name}")
        text = extract_text_from_image(img_file)
        transaction = parse_transaction_data(text, img_file.name)
        transaction['Source File'] = img_file.name
        transactions.append(transaction)
    
    return transactions


def generate_csv(transactions, output_file='transactions.csv'):
    """Generate CSV file with transaction data and totals"""
    if not transactions:
        print("No transactions to write!")
        return
    
    script_dir = Path(__file__).parent
    output_path = script_dir / output_file
    
    # Create DataFrame
    df = pd.DataFrame(transactions)
    
    # Reorder columns
    columns = ['Transaction Date', 'Amount Transferred', 'Transaction ID', 
               'Chit Amount', 'Source File']
    df = df[columns]
    
    # Calculate totals
    chit_total = df['Chit Amount'].sum()
    
    # Convert amount transferred to numeric for sum (handle potential string values)
    df['Amount Numeric'] = pd.to_numeric(df['Amount Transferred'].astype(str).str.replace(',', ''), 
                                         errors='coerce')
    amount_total = df['Amount Numeric'].sum()
    
    # Write to CSV
    df[columns].to_csv(output_path, index=False)
    
    # Append totals row
    with open(output_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([])  # Empty row
        writer.writerow(['TOTAL', f'{amount_total:,.2f}', '', f'{chit_total:,}', ''])
    
    print(f"\n✓ CSV file generated: {output_path}")
    print(f"  Total transactions: {len(transactions)}")
    print(f"  Total Chit Amount: ₹{chit_total:,}")
    print(f"  Total Amount Transferred: ₹{amount_total:,.2f}")
    
    return output_path


def main():
    """Main function to run the transaction parser"""
    print("=" * 60)
    print("Transaction Parser - Extracting data from images...")
    print("=" * 60)
    
    transactions = process_transactions()
    
    if transactions:
        generate_csv(transactions)
    else:
        print("No transactions found or processed.")


if __name__ == "__main__":
    main()
