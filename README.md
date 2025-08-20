# Auto Margin Report Automation

## FR-1: Get Processing Date from Email

This system automatically processes emails containing margin report requests, extracts date information, and converts it to NetSuite-compatible fiscal formats for report extraction.

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
- Python 3.7+
- pip package manager

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
NETSUITE_SECURITY_QUESTION=your_security_answer
```

## Configuration

### NetSuite Settings
- **URL**: `https://837809-sb1.app.netsuite.com/app/site/hosting/scriptlet.nl`
- **Script ID**: `1574`
- **Deploy ID**: `1`
- **Username**: `bill.li@hand-usa.com`

### Fiscal Calendar
- **Fiscal Year Start**: January (configurable)
- **Quarter Mapping**: 
  - Q1: Jan-Mar
  - Q2: Apr-Jun
  - Q3: Jul-Sep
  - Q4: Oct-Dec

## Usage

### Command Line Interface

#### Run the main application:
```bash
python main.py
```

#### Run tests:
```bash
python test_system.py
```

### Programmatic Usage

#### Process a single date:
```python
from main import MarginReportAutomation

automation = MarginReportAutomation()
result = automation.process_single_date("2025/08")
print(result['fiscal_summary'])  # FY 2025 : Q3 2025 : Aug 2025
```

#### Process an email:
```python
subject = "Margin Report"
body = "Please generate margin report for time range 08/2024 - 08/2025"
result = automation.process_email_request(subject, body)
```

## Architecture

### Core Modules

#### `date_parser.py`
- Handles date string parsing and validation
- Converts dates to fiscal formats
- Supports multiple input formats

#### `email_processor.py`
- Processes email content
- Validates email subjects
- Extracts time ranges from email bodies

#### `netsuite_client.py`
- Manages NetSuite authentication
- Constructs query URLs
- Handles secure credential storage

#### `config.py`
- Centralized configuration management
- Environment variable handling
- Security validation

#### `main.py`
- Main application orchestrator
- Workflow management
- Error handling and logging

## Security Features

- **Encrypted Credentials**: Sensitive data encrypted using Fernet encryption
- **Environment Variables**: Credentials stored in `.env` file (not in code)
- **Input Validation**: Comprehensive validation of all inputs
- **Error Logging**: Secure logging without exposing sensitive information

## Error Handling

### Input Validation
- Invalid date formats → User prompted to re-enter
- Invalid email subjects → Processing halted with error logging
- Missing credentials → Configuration validation fails

### Processing Errors
- Date parsing failures → Logged and processing halted
- NetSuite authentication failures → Retry logic and error logging
- Mapping failures → Comprehensive error reporting

## Logging

The system provides comprehensive logging:
- **File Logging**: `margin_report_automation.log`
- **Console Output**: Real-time status updates
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Secure Logging**: No sensitive data in logs

## Testing

### Test Coverage
- Date parsing functionality
- Email processing workflows
- NetSuite integration
- Error handling scenarios
- Fiscal calculations

### Running Tests
```bash
python test_system.py
```

## Example Workflow

1. **Email Received**: Subject: "Margin Report", Body: "time range 08/2024 - 08/2025"
2. **Subject Validation**: Confirms "Margin Report" in subject
3. **Date Extraction**: Parses "08/2024 - 08/2025"
4. **Fiscal Mapping**: 
   - Start: FY 2024 : Q3 2024 : Aug 2024
   - End: FY 2025 : Q3 2025 : Aug 2025
5. **NetSuite Query**: Constructs URL with fiscal parameters
6. **Authentication**: Secure login to NetSuite
7. **Report Generation**: Executes query with mapped parameters

## Output Format

### Fiscal Summary
```
FY 2024 : Q3 2024 : Aug 2024 to FY 2025 : Q3 2025 : Aug 2025
```

### NetSuite Query Parameters
- `fiscal_year`: FY 2025
- `quarter`: Q3 2025
- `month`: Aug 2025
- `year`: 2025
- `quarter_num`: 3
- `month_num`: 08

## Troubleshooting

### Common Issues

#### Configuration Errors
- **Missing .env file**: Copy `env_example.txt` to `.env`
- **Invalid credentials**: Verify NetSuite username/password
- **Missing dependencies**: Run `pip install -r requirements.txt`

#### Date Parsing Issues
- **Unsupported format**: Use supported formats (YYYY/MM, MM/YYYY)
- **Invalid dates**: Ensure month is 1-12, year is reasonable

#### NetSuite Integration Issues
- **Authentication failures**: Verify credentials and security question
- **URL construction errors**: Check script and deploy IDs

### Debug Mode
Enable debug logging by setting `LOG_LEVEL=DEBUG` in `.env`

## Contributing

1. Follow the existing code structure
2. Add comprehensive error handling
3. Include logging for all operations
4. Write tests for new functionality
5. Update documentation

## License

[Add your license information here]

## Support

For technical support or questions about the system, please contact the development team.
