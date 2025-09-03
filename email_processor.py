import re
import logging
from typing import Dict, Optional, Tuple
from date_parser import DateParser
from config import Config

logger = logging.getLogger(__name__)

class EmailProcessor:
    """Process emails to extract date information for margin reports"""
    
    def __init__(self):
        """Initialize EmailProcessor with date parser"""
        self.date_parser = DateParser(Config.FISCAL_YEAR_START_MONTH)
        self.subject_pattern = Config.EMAIL_SUBJECT_PATTERN
    
    def process_email(self, email_subject: str, email_body: str) -> Optional[Dict]:
        """
        Process email to extract date information
        
        Args:
            email_subject: Email subject line
            email_body: Email body text
            
        Returns:
            Dictionary with extracted information or None if processing fails
        """
        try:
            # Extract date-related information using regex
            fiscal_start_match = re.search(r'Fiscal Year Starts From Which Month: (\d+)', email_body)
            period_from_year_match = re.search(r'Period From\(Year\): (\d+)', email_body)
            period_from_month_match = re.search(r'Period From\(Month\): (\d+)', email_body)
            period_to_year_match = re.search(r'Period To\(Year\): (\d+)', email_body)
            period_to_month_match = re.search(r'Period To\(Month\): (\d+)', email_body)

            # List to collect missing or invalid fields
            invalid_fields = []

            def extract_int(match, field_name):
                if match:
                    try:
                        return int(match.group(1))
                    except ValueError:
                        invalid_fields.append(field_name)
                        return None
                else:
                    invalid_fields.append(field_name)
                    return None

            # Extract and validate each value
            fiscal_start = extract_int(fiscal_start_match, 'fiscal_start')
            period_from_year = extract_int(period_from_year_match, 'period_from_year')
            period_from_month = extract_int(period_from_month_match, 'period_from_month')
            period_to_year = extract_int(period_to_year_match, 'period_to_year')
            period_to_month = extract_int(period_to_month_match, 'period_to_month')

            if invalid_fields:
                logger.error(f"Missing or invalid fields in email body: {', '.join(invalid_fields)}")
                return None

            # Format dates for NetSuite
            start_date = {
                'fiscal_year': str(period_from_year),
                'month': str(period_from_month).zfill(2),
                'quarter': self._calculate_quarter(period_from_month, fiscal_start)
            }

            end_date = {
                'fiscal_year': str(period_to_year),
                'month': str(period_to_month).zfill(2),
                'quarter': self._calculate_quarter(period_to_month, fiscal_start)
            }

            # Create result with all necessary information
            result = {
                'email_subject': email_subject,
                'start_date': start_date,
                'end_date': end_date,
                'fiscal_summary': self._create_fiscal_summary(start_date, end_date),
                'processing_status': 'success'
            }

            logger.info(f"Successfully processed email: {result['fiscal_summary']}")
            return result

        except Exception as e:
            logger.error(f"Unexpected error while processing email: {str(e)}")
            return None
    
    def _validate_subject(self, subject: str) -> bool:
        """
        Validate email subject matches expected pattern
        
        Args:
            subject: Email subject line
            
        Returns:
            True if subject is valid, False otherwise
        """
        if not subject:
            return False
        
        # Check if subject contains the expected pattern
        return self.subject_pattern.lower() in subject.lower()
    
    def _create_fiscal_summary(self, start_date: Dict, end_date: Dict) -> str:
        """
        Create a summary of fiscal parameters
        
        Args:
            start_date: Start date fiscal parameters
            end_date: End date fiscal parameters
            
        Returns:
            Formatted fiscal summary string
        """
        start_summary = f"{start_date['fiscal_year']} : {start_date['quarter']} : {start_date['month']}"
        end_summary = f"{end_date['fiscal_year']} : {end_date['quarter']} : {end_date['month']}"
        
        return f"{start_summary} to {end_summary}"
    
    def extract_single_date(self, date_string: str) -> Optional[Dict]:
        """
        Extract fiscal parameters from a single date string
        
        Args:
            date_string: Date string (e.g., "2025/08", "08/2025")
            
        Returns:
            Dictionary with fiscal parameters or None if parsing fails
        """
        try:
            result = self.date_parser.parse_date_string(date_string)
            if result:
                logger.info(f"Successfully parsed single date: {date_string} -> {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to parse single date '{date_string}': {str(e)}")
            return None
    
    def validate_date_format(self, date_string: str) -> bool:
        """
        Validate if a date string is in a supported format
        
        Args:
            date_string: Date string to validate
            
        Returns:
            True if format is supported, False otherwise
        """
        try:
            result = self.date_parser.parse_date_string(date_string)
            return result is not None
        except:
            return False
    
    def get_supported_formats(self) -> list:
        """Get list of supported date formats"""
        return [
            "YYYY/MM (e.g., 2025/08)",
            "MM/YYYY (e.g., 08/2025)",
            "YYYY-MM (e.g., 2025-08)",
            "MM-YYYY (e.g., 08-2025)"
        ]
