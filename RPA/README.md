# Auto Margin Report Automation

## FR-1: Get Processing Date from Email

This system automatically processes emails containing margin report requests, extracts date information, and converts it to NetSuite-compatible fiscal formats for report extraction.

## FR-2: Automated Report Extraction (RPA)

Automates downloading quarterly margin reports from NetSuite using Selenium-driven RPA.

### Inputs
- Date range (start, end): e.g. 2024-01-01 to 2025-06-30
- NetSuite Saved Search ID
- NetSuite URL/Script/Deploy (configured in `config.py`)

### Processing
1. Parse input date range, enumerate all included quarters
2. For each quarter:
   - Build quarter-specific date filter (YYYY-MM-DD to YYYY-MM-DD)
   - Login to NetSuite
   - Open scriptlet URL with query params (saved search + date range)
   - Trigger export to XLS
   - Save to `temp_downloads/margin_{YYYY}_Q{n}.xls`
3. Continue on failure; log and move to next quarter

### Output
- XLS files per quarter in `temp_downloads/`

### Run
```bash
# Example
python3 fr2_run.py --start 2024-01-01 --end 2025-06-30 --saved_search_id 123 --headless
```

### Notes
- This flow uses Selenium with Chrome. Ensure you have a compatible Chrome/ChromeDriver setup (or use webdriver-manager).
- Selectors for login/export are placeholders and may need adjustment to your NetSuite UI/customizations.
- Security question answers can be provided via env vars `NS_SQ_1`, `NS_SQ_2`, `NS_SQ_3`.

---

## Features

### Core Functionality
- **Email Processing**: Automatically extracts date information from emails with "Margin Report" subject
- **Date Parsing**: Supports multiple date formats (YYYY/MM, MM/YYYY, YYYY-MM, MM-YYYY)
- **Fiscal Mapping**: Converts dates to NetSuite fiscal formats:
  - Fiscal Year (FY): Based on company fiscal calendar
  - Quarter (Q): Automatic quarter calculation
  - Month Name (MMM): Three-letter month abbreviations
- **NetSuite Integration**: Constructs query URLs with fiscal parameters
- **Secure Authentication**: Encrypted credential handling
- **RPA Downloader (FR-2)**: Automates quarterly report exports to XLS

### Supported Date Formats
- `2025/08` → FY 2025 : Q3 2025 : Aug 2025
- `08/2025` → FY 2025 : Q3 2025 : Aug 2025
- `2025-08` → FY 2025 : Q3 2025 : Aug 2025
- `08-2025` → FY 2025 : Q3 2025 : Aug 2025

### Email Processing
- **Subject Validation**: Must contain "Margin Report"
- **Body Parsing**: Extracts time ranges (e.g., "08/2024 - 08/2025")
- **Automatic Mapping**: Converts to fiscal parameters for NetSuite queries

## Installation

### Prerequisites
- Python 3.8+
- Google Chrome installed (for RPA)
- ChromeDriver available in PATH (or adapt `rpa_downloader.py` to use webdriver-manager)

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd Auto_Margin_Report_Automation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp env_example.txt .env
# Edit .env with your NetSuite credentials
```

4. Update `.env` file with your credentials:
```bash
NETSUITE_USERNAME=bill.li@hand-usa.com
NETSUITE_PASSWORD=your_actual_password
NS_SQ_1=mochi
NS_SQ_2=boston
NS_SQ_3=sanjose
```

## Usage

### FR-1 CLI (email parsing only)
```bash
python3 parse_from_email.py --body "time range 08/2024 - 08/2025" --pretty
```

### FR-2 CLI (RPA quarterly downloads)
```bash
python3 fr2_run.py --start 2024-01-01 --end 2025-06-30 --saved_search_id 123 --headless
```

## Architecture

### Core Modules

#### `