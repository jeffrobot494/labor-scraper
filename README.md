# Form 5500 Data Analysis Tools

This repository contains Python tools for analyzing Form 5500 datasets from the Department of Labor.

## Tools

### 1. Form 5500 Dataset Analyzer

Analyzes datasets to find sponsor information using fuzzy matching.

```bash
# Basic usage with default values
python form5500_analysis.py

# Specify a different dataset URL
python form5500_analysis.py --url "https://askebsa.dol.gov/FOIA%20Files/2022/Latest/F_5500_2022_Latest.zip"

# Search for a different company
python form5500_analysis.py --sponsor "MICROSOFT CORPORATION"

# Adjust the similarity threshold for matching
python form5500_analysis.py --threshold 75
```

### 2. EFAST2 Form 5500 Scraper

Uses Selenium to automate downloading Form 5500 filings from the DOL's EFAST2 search portal.

```bash
# Basic usage with default filing ID
python efast2_scraper.py

# Specify a different filing ID
python efast2_scraper.py --filing-id 20230924160904NAL0004813043001
```

### 3. Form 5500 PDF Parser

Downloads Form 5500 filings and extracts Schedule A information, including premium data.

```bash
# Basic usage with default filing ID
python form5500_scraper.py

# Specify a different filing ID
python form5500_scraper.py --filing-id 20230924160904NAL0004813043001
```

## Requirements

- Python 3.7 or higher
- Required packages:
  - requests
  - pandas
  - rapidfuzz
  - pdfplumber
  - selenium

## Installation

1. Clone this repository or download the files
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage Notes

### Dataset Analyzer
- Downloads and analyzes Form 5500 datasets from the Department of Labor
- Uses fuzzy matching to find sponsor names that match a target
- Displays key information from matching records including EIN and ACK_ID

### EFAST2 Scraper
- Uses Selenium to automate browser interaction with DOL's EFAST2 portal
- Searches for filings by ACK_ID
- Downloads filing ZIP files and extracts their contents
- Supports headless operation with automatic download handling

### PDF Parser
- Downloads individual Form 5500 filings by ID
- Extracts Schedule A forms from the filing PDF
- Parses premium information, insurance carrier names, and broker details
- Outputs a summary of extracted information

## Data Storage

- Downloaded and extracted files are stored in a `data` directory for the dataset analyzer
- Downloaded filings are stored in a `downloads` directory for the filing scraper

## Error Handling

Both tools include error handling for:
- Failed downloads
- Invalid files
- Parsing errors