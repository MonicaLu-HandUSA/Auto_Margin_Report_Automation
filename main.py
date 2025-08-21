"""
Main application for Auto Margin Report Automation
FR-1: Get Processing date from Email
"""

import logging
import sys
from typing import Dict, Optional
from email_processor import EmailProcessor
from netsuite_client import NetSuiteClient
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class MarginReportAutomation:
    """Main class for automating margin report processing"""
    
    def __init__(self):
        """Initialize the automation system"""
        try:
            # Validate configuration
            Config.validate_config()
            
            # Initialize components
            self.email_processor = EmailProcessor()
            self.netsuite_client = NetSuiteClient()
            
            logger.info("Margin Report Automation system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {str(e)}")
            raise
    
    def process_email_request(self, email_subject: str, email_body: str, 
                           saved_search_id: str = None) -> Optional[Dict]:
        """
        Process email request and execute NetSuite query
        
        Args:
            email_subject: Email subject line
            email_body: Email body text
            saved_search_id: Optional NetSuite saved search ID
            
        Returns:
            Processing results or None if processing fails
        """
        try:
            logger.info("Starting email processing workflow")
            
            # Step 1: Process email to extract date information
            email_result = self.email_processor.process_email(email_subject, email_body)
            if not email_result:
                logger.error("Email processing failed")
                return None
            
            logger.info(f"Email processed successfully: {email_result['fiscal_summary']}")
            
            # Step 2: Execute NetSuite query for start date
            start_date_params = email_result['start_date']
            netsuite_result = self.netsuite_client.execute_query(
                start_date_params, saved_search_id
            )
            
            if not netsuite_result:
                logger.error("NetSuite query execution failed")
                return None
            
            # Step 3: Compile final results
            final_result = {
                'email_processing': email_result,
                'netsuite_query': netsuite_result,
                'overall_status': 'success',
                'fiscal_summary': email_result['fiscal_summary']
            }
            
            logger.info("Email processing workflow completed successfully")
            return final_result
            
        except Exception as e:
            logger.error(f"Email processing workflow failed: {str(e)}")
            return None
    
    def process_single_date(self, date_string: str, saved_search_id: str = None) -> Optional[Dict]:
        """
        Process a single date string and execute NetSuite query
        
        Args:
            date_string: Date string (e.g., "2025/08", "08/2025")
            saved_search_id: Optional NetSuite saved search ID
            
        Returns:
            Processing results or None if processing fails
        """
        try:
            logger.info(f"Processing single date: {date_string}")
            
            # Extract fiscal parameters
            fiscal_params = self.email_processor.extract_single_date(date_string)
            if not fiscal_params:
                logger.error(f"Failed to parse date: {date_string}")
                return None
            
            # Execute NetSuite query
            netsuite_result = self.netsuite_client.execute_query(
                fiscal_params, saved_search_id
            )
            
            if not netsuite_result:
                logger.error("NetSuite query execution failed")
                return None
            
            # Compile results
            result = {
                'date_input': date_string,
                'fiscal_params': fiscal_params,
                'netsuite_query': netsuite_result,
                'fiscal_summary': self.netsuite_client.get_fiscal_summary(fiscal_params),
                'status': 'success'
            }
            
            logger.info(f"Single date processing completed: {result['fiscal_summary']}")
            return result
            
        except Exception as e:
            logger.error(f"Single date processing failed: {str(e)}")
            return None
    
    def get_system_status(self) -> Dict:
        """Get system status and configuration information"""
        try:
            status = {
                'system_status': 'operational',
                'configuration': {
                    'netsuite_url': Config.NETSUITE_URL,
                    'fiscal_year_start_month': Config.FISCAL_YEAR_START_MONTH,
                    'email_subject_pattern': Config.EMAIL_SUBJECT_PATTERN
                },
                'supported_date_formats': self.email_processor.get_supported_formats(),
                'timestamp': logging.Formatter().formatTime(logging.LogRecord(
                    'status', logging.INFO, '', 0, '', (), None
                ))
            }
            
            logger.info("System status retrieved successfully")
            return status
            
        except Exception as e:
            logger.error(f"Failed to get system status: {str(e)}")
            return {'system_status': 'error', 'error': str(e)}

def main():
    """Main function for command-line usage"""
    try:
        # Initialize system
        automation = MarginReportAutomation()
        
        # Example usage
        print("=== Margin Report Automation System ===")
        print("FR-1: Get Processing date from Email")
        print()
        
        # Get system status
        status = automation.get_system_status()
        print(f"System Status: {status['system_status']}")
        print(f"NetSuite URL: {status['configuration']['netsuite_url']}")
        print()
        
        # Example: Process single date
        test_date = "2025/08"
        print(f"Testing single date processing: {test_date}")
        result = automation.process_single_date(test_date)
        
        if result:
            print(f"✓ Date processed successfully")
            print(f"  Fiscal Summary: {result['fiscal_summary']}")
            print(f"  NetSuite URL: {result['netsuite_query']['query_url']}")
        else:
            print("✗ Date processing failed")
        
        print()
        
        # Example: Process email
        test_subject = "Margin Report"
        test_body = "Please generate margin report for time range 08/2024 - 08/2025"
        print(f"Testing email processing:")
        print(f"  Subject: {test_subject}")
        print(f"  Body: {test_body}")
        
        email_result = automation.process_email_request(test_subject, test_body)
        
        if email_result:
            print(f"✓ Email processed successfully")
            print(f"  Fiscal Summary: {email_result['fiscal_summary']}")
        else:
            print("✗ Email processing failed")
        
        print()
        print("System ready for production use!")
        
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
