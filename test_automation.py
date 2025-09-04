#!/usr/bin/env python3
import logging
from rpa_downloader import NetSuiteRPADownloader
from email_processor import EmailProcessor
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_with_sample_email():
    """Test automation with sample email content"""
    # Sample email content for testing
    test_email = {
        'subject': 'Margin Report',
        'body': '''
        Fiscal Year Starts From Which Month: 01
        Period From(Year): 2024
        Period From(Month): 08
        Period To(Year): 2025
        Period To(Month): 08
        '''
    }
    
    try:
        # 1. Process email
        processor = EmailProcessor()
        result = processor.process_email(test_email['subject'], test_email['body'])
        
        if not result:
            logger.error("Failed to process email")
            return
            
        logger.info("Email processing result:")
        logger.info(f"Fiscal Summary: {result['fiscal_summary']}")
        logger.info(f"Start Date: {result['start_date']}")
        logger.info(f"End Date: {result['end_date']}")
        
        # 2. Test NetSuite automation
        logger.info("\nTesting NetSuite automation...")
        downloader = NetSuiteRPADownloader(headless=False)  # Set to False to see the browser
        
        # Login to NetSuite
        downloader.login()
        
        # Test security questions (this will print page source and save screenshot)
        logger.info("\nTesting security questions...")
        downloader.test_security_questions()
        
        # Select dates and download
        logger.info("\nSelecting dates...")
        success = downloader._select_dates_and_download(
            result['start_date'],
            result['end_date']
        )
        
        if success:
            logger.info("Successfully completed automation test")
        else:
            logger.error("Failed to complete automation test")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
    finally:
        # Cleanup
        if 'downloader' in locals() and downloader.driver:
            downloader.driver.quit()

def main():
    """Main test function"""
    print("=== Auto Margin Report Automation Test ===")
    print("\nThis test will:")
    print("1. Process a sample email")
    print("2. Login to NetSuite")
    print("3. Test security question handling")
    print("4. Attempt to fill date dropdowns")
    print("\nPress Enter to start the test (Ctrl+C to cancel)")
    
    try:
        input()
        test_with_sample_email()
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
    except Exception as e:
        print(f"\nTest failed: {str(e)}")

if __name__ == "__main__":
    main()
