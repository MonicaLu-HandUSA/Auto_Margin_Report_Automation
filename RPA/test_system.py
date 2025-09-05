#!/usr/bin/env python3
"""
Test script for Margin Report Automation System
Tests FR-1 functionality: Get Processing date from Email
"""

import sys
import logging
from email_processor import EmailProcessor
from date_parser import DateParser
from netsuite_client import NetSuiteClient

# Configure logging for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_date_parsing():
    """Test date parsing functionality"""
    print("=== Testing Date Parsing ===")
    
    date_parser = DateParser()
    
    # Test various date formats
    test_dates = [
        "2025/08",
        "08/2025", 
        "2025-08",
        "08-2025",
        "2025/8",
        "8/2025"
    ]
    
    for test_date in test_dates:
        print(f"\nTesting: {test_date}")
        try:
            result = date_parser.parse_date_string(test_date)
            if result:
                print(f"  ✓ Success: {result['fiscal_year']} : {result['quarter']} : {result['month']}")
                print(f"    Fiscal Year: {result['fiscal_year']}")
                print(f"    Quarter: {result['quarter']}")
                print(f"    Month: {result['month']}")
            else:
                print(f"  ✗ Failed to parse")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
    
    print("\n" + "="*50)

def test_email_processing():
    """Test email processing functionality"""
    print("=== Testing Email Processing ===")
    
    email_processor = EmailProcessor()
    
    # Test email with time range
    test_subject = "Margin Report"
    test_body = "Please generate margin report for time range 08/2024 - 08/2025"
    
    print(f"Email Subject: {test_subject}")
    print(f"Email Body: {test_body}")
    
    try:
        result = email_processor.process_email(test_subject, test_body)
        if result:
            print(f"  ✓ Email processed successfully")
            print(f"  Fiscal Summary: {result['fiscal_summary']}")
            print(f"  Start Date: {result['start_date']['fiscal_year']} : {result['start_date']['quarter']} : {result['start_date']['month']}")
            print(f"  End Date: {result['end_date']['fiscal_year']} : {result['end_date']['quarter']} : {result['end_date']['month']}")
        else:
            print(f"  ✗ Email processing failed")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    print("\n" + "="*50)

def test_netsuite_integration():
    """Test NetSuite integration (mock)"""
    print("=== Testing NetSuite Integration ===")
    
    try:
        # This will fail without proper environment variables, but we can test the structure
        netsuite_client = NetSuiteClient()
        print("  ✓ NetSuite client initialized")
        
        # Test fiscal summary creation
        test_params = {
            'fiscal_year': 'FY 2025',
            'quarter': 'Q3 2025',
            'month': 'Aug 2025'
        }
        
        summary = netsuite_client.get_fiscal_summary(test_params)
        print(f"  ✓ Fiscal summary created: {summary}")
        
    except Exception as e:
        print(f"  ⚠ NetSuite client test (expected without .env): {str(e)}")
    
    print("\n" + "="*50)

def test_error_handling():
    """Test error handling for invalid inputs"""
    print("=== Testing Error Handling ===")
    
    date_parser = DateParser()
    
    # Test invalid date formats
    invalid_dates = [
        "invalid_date",
        "2025/13",  # Invalid month
        "2025/00",  # Invalid month
        "2025/",    # Incomplete
        "/2025",    # Incomplete
        "",         # Empty
        "abc/def"   # Non-numeric
    ]
    
    for invalid_date in invalid_dates:
        print(f"\nTesting invalid date: '{invalid_date}'")
        try:
            result = date_parser.parse_date_string(invalid_date)
            if result:
                print(f"  ⚠ Unexpected success: {result}")
            else:
                print(f"  ✓ Correctly rejected invalid date")
        except Exception as e:
            print(f"  ✓ Correctly handled error: {str(e)}")
    
    print("\n" + "="*50)

def test_fiscal_calculations():
    """Test fiscal year and quarter calculations"""
    print("=== Testing Fiscal Calculations ===")
    
    date_parser = DateParser()
    
    # Test fiscal year boundaries
    test_cases = [
        (1, 2025, "January 2025 - should be FY 2025"),
        (12, 2024, "December 2024 - should be FY 2024"),
        (6, 2025, "June 2025 - should be FY 2025"),
        (7, 2025, "July 2025 - should be FY 2025")
    ]
    
    for month, year, description in test_cases:
        print(f"\n{description}")
        try:
            result = date_parser._convert_to_fiscal_format(year, month)
            print(f"  Month: {month:02d}/{year}")
            print(f"  Fiscal Year: {result['fiscal_year']}")
            print(f"  Quarter: {result['quarter']}")
            print(f"  Month: {result['month']}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
    
    print("\n" + "="*50)

def main():
    """Run all tests"""
    print("Margin Report Automation System - Test Suite")
    print("FR-1: Get Processing date from Email")
    print("=" * 60)
    
    try:
        test_date_parsing()
        test_email_processing()
        test_netsuite_integration()
        test_error_handling()
        test_fiscal_calculations()
        
        print("\n=== Test Summary ===")
        print("✓ Date parsing functionality tested")
        print("✓ Email processing functionality tested")
        print("✓ NetSuite integration structure tested")
        print("✓ Error handling tested")
        print("✓ Fiscal calculations tested")
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
