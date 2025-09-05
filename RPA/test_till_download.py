import sys
import time
import logging
from config import Config
from rpa_downloader import NetSuiteRPADownloader
from email_processor import EmailProcessor
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

def main():
    """Main function combining email parse + NetSuite login + security Q + download"""

    print("=== Margin Report Automation Full Test ===")
    try:
        # 1. Process email
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
        print("\n[Step 1] Processing email request...")
        processor = EmailProcessor()
        email_result = processor.process_email(test_email['subject'], test_email['body'])

        if not email_result:
            print("✗ Email parsing failed")
            return
        print("✓ Email parsed successfully")
        print(f"  Fiscal Summary: {email_result['fiscal_summary']}")
        print(f"  Start Date: {email_result['start_date']}")
        print(f"  End Date: {email_result['end_date']}")

        # 2. Login to NetSuite (including security questions)
        print("\n[Step 2] Logging into NetSuite...")
        start_url = f"{Config.NETSUITE_URL}?script={Config.NETSUITE_SCRIPT_ID}&deploy={Config.NETSUITE_DEPLOY_ID}&whence="
        downloader = NetSuiteRPADownloader(headless=False)
        downloader.login(start_url=start_url)
        print("Now at:", downloader.driver.current_url)

        # Handle security questions
        print("\n[Step 3] Handling security questions...")
        downloader._handle_security_questions()

        # 3. Select dates and download
        print("\n[Step 4] Selecting dates and downloading report...")
        success = downloader._handle_download_page(
            email_result['start_date'],
            email_result['end_date']
        )

        if success:
            print("✓ Successfully initiated download")
        else:
            print("✗ Failed to download report")

    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        if 'downloader' in locals() and downloader.driver:
            downloader.driver.quit()
        print("\n=== Test Finished ===")


if __name__ == "__main__":
    main()
