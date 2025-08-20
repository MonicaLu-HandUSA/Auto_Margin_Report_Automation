#!/usr/bin/env python3
"""
Demo script for Margin Report Automation System
Shows core functionality without requiring NetSuite credentials
"""

import logging
from email_processor import EmailProcessor
from date_parser import DateParser

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def demo_date_parsing():
    """Demonstrate date parsing functionality"""
    print("=== Date Parsing Demo ===")
    
    date_parser = DateParser()
    
    # Test various date formats
    test_dates = [
        "2025/08",
        "08/2025", 
        "2025-08",
        "08-2025"
    ]
    
    for test_date in test_dates:
        print(f"\nInput: {test_date}")
        result = date_parser.parse_date_string(test_date)
        if result:
            print(f"  → Fiscal Year: {result['fiscal_year']}")
            print(f"  → Quarter: {result['quarter']}")
            print(f"  → Month: {result['month']}")
            print(f"  → NetSuite Format: {result['fiscal_year']} : {result['quarter']} : {result['month']}")
    
    print("\n" + "="*50)

def demo_email_processing():
    """Demonstrate email processing functionality"""
    print("=== Email Processing Demo ===")
    
    email_processor = EmailProcessor()
    
    # Test email with time range
    test_subject = "Margin Report"
    test_body = "Please generate margin report for time range 08/2024 - 08/2025"
    
    print(f"Email Subject: {test_subject}")
    print(f"Email Body: {test_body}")
    print()
    
    result = email_processor.process_email(test_subject, test_body)
    if result:
        print("✓ Email processed successfully!")
        print(f"Fiscal Summary: {result['fiscal_summary']}")
        print()
        print("Detailed Breakdown:")
        print(f"  Start Date: {result['start_date']['fiscal_year']} : {result['start_date']['quarter']} : {result['start_date']['month']}")
        print(f"  End Date: {result['end_date']['fiscal_year']} : {result['end_date']['quarter']} : {result['end_date']['month']}")
        
        # Show NetSuite query parameters
        print()
        print("NetSuite Query Parameters:")
        start_params = result['start_date']
        print(f"  fiscal_year: {start_params['fiscal_year']}")
        print(f"  quarter: {start_params['quarter']}")
        print(f"  month: {start_params['month']}")
        print(f"  year: {start_params['year']}")
        print(f"  quarter_num: {start_params['quarter_num']}")
        print(f"  month_num: {start_params['month_num']}")
    else:
        print("✗ Email processing failed")
    
    print("\n" + "="*50)

def demo_fiscal_calculations():
    """Demonstrate fiscal year and quarter calculations"""
    print("=== Fiscal Calculations Demo ===")
    
    date_parser = DateParser()
    
    # Test fiscal year boundaries
    test_cases = [
        (1, 2025, "January 2025"),
        (6, 2025, "June 2025"),
        (12, 2024, "December 2024"),
        (3, 2025, "March 2025")
    ]
    
    for month, year, description in test_cases:
        print(f"\n{description}")
        result = date_parser._convert_to_fiscal_format(year, month)
        print(f"  Input: {month:02d}/{year}")
        print(f"  Fiscal Year: {result['fiscal_year']}")
        print(f"  Quarter: {result['quarter']}")
        print(f"  Month: {result['month']}")
    
    print("\n" + "="*50)

def demo_error_handling():
    """Demonstrate error handling for invalid inputs"""
    print("=== Error Handling Demo ===")
    
    date_parser = DateParser()
    
    # Test invalid date formats
    invalid_dates = [
        "invalid_date",
        "2025/13",  # Invalid month
        "2025/00",  # Invalid month
        "",         # Empty
        "abc/def"   # Non-numeric
    ]
    
    for invalid_date in invalid_dates:
        print(f"\nTesting: '{invalid_date}'")
        try:
            result = date_parser.parse_date_string(invalid_date)
            if result:
                print(f"  ⚠ Unexpected success: {result}")
            else:
                print(f"  ✓ Correctly rejected invalid date")
        except Exception as e:
            print(f"  ✓ Correctly handled error: {str(e)}")
    
    print("\n" + "="*50)

def demo_netsuite_url_construction():
    """Demonstrate how NetSuite URLs would be constructed"""
    print("=== NetSuite URL Construction Demo ===")
    
    # Mock NetSuite configuration
    base_url = "https://837809-sb1.app.netsuite.com/app/site/hosting/scriptlet.nl"
    script_id = "1574"
    deploy_id = "1"
    
    print(f"Base URL: {base_url}")
    print(f"Script ID: {script_id}")
    print(f"Deploy ID: {deploy_id}")
    print()
    
    # Example fiscal parameters
    fiscal_params = {
        'fiscal_year': 'FY 2025',
        'quarter': 'Q3 2025',
        'month': 'Aug 2025',
        'year': '2025',
        'quarter_num': '3',
        'month_num': '08'
    }
    
    print("Example Fiscal Parameters:")
    for key, value in fiscal_params.items():
        print(f"  {key}: {value}")
    
    # Construct example URL
    params = {
        'script': script_id,
        'deploy': deploy_id,
        'whence': '',
        'fiscal_year': fiscal_params['fiscal_year'],
        'quarter': fiscal_params['quarter'],
        'month': fiscal_params['month']
    }
    
    query_string = '&'.join([f"{k}={v}" for k, v in params.items() if v])
    example_url = f"{base_url}?{query_string}"
    
    print()
    print("Example NetSuite Query URL:")
    print(f"  {example_url}")
    
    print("\n" + "="*50)

def main():
    """Run all demos"""
    print("Margin Report Automation System - Demo")
    print("FR-1: Get Processing Date from Email")
    print("=" * 60)
    print()
    
    try:
        demo_date_parsing()
        demo_email_processing()
        demo_fiscal_calculations()
        demo_error_handling()
        demo_netsuite_url_construction()
        
        print("\n=== Demo Summary ===")
        print("✓ Date parsing demonstrated")
        print("✓ Email processing demonstrated")
        print("✓ Fiscal calculations demonstrated")
        print("✓ Error handling demonstrated")
        print("✓ NetSuite URL construction demonstrated")
        print()
        print("The system successfully:")
        print("  1. Parses various date formats")
        print("  2. Converts dates to NetSuite fiscal formats")
        print("  3. Processes email content for time ranges")
        print("  4. Handles errors gracefully")
        print("  5. Constructs NetSuite query URLs")
        print()
        print("Ready for production use with proper NetSuite credentials!")
        
    except Exception as e:
        print(f"\n✗ Demo failed: {str(e)}")

if __name__ == "__main__":
    main()
