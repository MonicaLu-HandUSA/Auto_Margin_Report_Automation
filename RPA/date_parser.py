import re
from datetime import datetime, date
from dateutil import parser
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class DateParser:
    """Parser for converting date strings to NetSuite fiscal formats"""
    
    def __init__(self, fiscal_year_start_month: int = 1):
        """
        Initialize DateParser with fiscal year configuration
        
        Args:
            fiscal_year_start_month: Month when fiscal year starts (1-12, default: 1 for January)
        """
        self.fiscal_year_start_month = fiscal_year_start_month
        self.date_patterns = [
            r'(\d{4})/(\d{1,2})',  # 2025/08 or 2025/8
            r'(\d{1,2})/(\d{4})',  # 08/2025 or 8/2025
            r'(\d{1,2})-(\d{4})',  # 08-2025 or 8-2025
            r'(\d{4})-(\d{1,2})',  # 2025-08 or 2025-8
        ]
    
    def parse_date_string(self, date_string: str) -> Optional[Dict[str, str]]:
        """
        Parse date string and return fiscal parameters
        
        Args:
            date_string: Date string in various formats (e.g., "2025/08", "08/2025")
            
        Returns:
            Dictionary with fiscal parameters or None if parsing fails
        """
        try:
            # Clean the input string
            date_string = date_string.strip()
            
            # Try to match known patterns
            for pattern in self.date_patterns:
                match = re.match(pattern, date_string)
                if match:
                    groups = match.groups()
                    if len(groups) == 2:
                        if len(groups[0]) == 4:  # First group is year
                            year = int(groups[0])
                            month = int(groups[1])
                        else:  # First group is month
                            month = int(groups[0])
                            year = int(groups[1])
                        
                        return self._convert_to_fiscal_format(year, month)
            
            # If no pattern matches, try dateutil parser
            parsed_date = parser.parse(date_string, fuzzy=True)
            return self._convert_to_fiscal_format(parsed_date.year, parsed_date.month)
            
        except Exception as e:
            logger.error(f"Failed to parse date string '{date_string}': {str(e)}")
            return None
    
    def _convert_to_fiscal_format(self, year: int, month: int) -> Dict[str, str]:
        """
        Convert year and month to NetSuite fiscal format for dropdown selection
        
        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)
            
        Returns:
            Dictionary with fiscal parameters formatted for NetSuite dropdowns
        """
        try:
            # Validate inputs
            if not (1 <= month <= 12):
                raise ValueError(f"Invalid month: {month}")
            if year < 1900 or year > 2100:
                raise ValueError(f"Invalid year: {year}")
            
            # Calculate fiscal year
            fiscal_year = self._calculate_fiscal_year(year, month)
            
            # Calculate quarter
            quarter = self._calculate_quarter(month)
            
            # Get month abbreviation
            month_abbr = self._get_month_abbreviation(month)
            
            # Format for NetSuite dropdown (FY 2025 : Q3 2025 : Aug 2025)
            netsuite_format = f"FY {fiscal_year} : Q{quarter} {fiscal_year} : {month_abbr} {fiscal_year}"
            
            result = {
                'fiscal_year': f"FY {fiscal_year}",
                'quarter': f"Q{quarter} {fiscal_year}",
                'month': f"{month_abbr} {fiscal_year}",
                'year': str(fiscal_year),
                'quarter_num': str(quarter),
                'month_num': f"{month:02d}",
                'original_year': str(year),
                'original_month': str(month),
                'netsuite_dropdown_value': netsuite_format
            }
            
            logger.info(f"Successfully converted {month:02d}/{year} to fiscal format: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to convert to fiscal format: {str(e)}")
            raise
    
    def _calculate_fiscal_year(self, year: int, month: int) -> int:
        """Calculate fiscal year based on fiscal year start month"""
        if month >= self.fiscal_year_start_month:
            return year
        else:
            return year - 1
    
    def _calculate_quarter(self, month: int) -> int:
        """
        Calculate quarter based on month and fiscal year start
        
        Args:
            month: Month (1-12)
            
        Returns:
            Quarter number (1-4)
        """
        months_since_fiscal_start = (month - self.fiscal_year_start_month) % 12
        return (months_since_fiscal_start // 3) + 1
    
    def _get_month_abbreviation(self, month: int) -> str:
        """Get month abbreviation (e.g., 1 -> Jan)"""
        month_names = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        return month_names[month - 1]
    
    def parse_email_time_range(self, email_body: str) -> Optional[Dict]:
        """
        Parse time range from email body with fiscal year consideration
        
        Args:
            email_body: Email body text containing fiscal year start and date range
            
        Returns:
            Dictionary with start and end date information or None if parsing fails
        """
        try:
            # Extract fiscal year start month
            fiscal_start_match = re.search(r'Fiscal Year Starts From Which Month: (\d+)', email_body)
            if not fiscal_start_match:
                logger.error("Could not find fiscal year start month in email")
                return None
            
            # Extract period information
            from_year = re.search(r'Period From\(Year\): (\d+)', email_body)
            from_month = re.search(r'Period From\(Month\): (\d+)', email_body)
            to_year = re.search(r'Period To\(Year\): (\d+)', email_body)
            to_month = re.search(r'Period To\(Month\): (\d+)', email_body)
            
            if not all([from_year, from_month, to_year, to_month]):
                logger.error("Could not find all required date components in email")
                return None
            
            # Update fiscal year start month
            self.fiscal_year_start_month = int(fiscal_start_match.group(1))
            
            # Process start date
            start_date = self._convert_to_fiscal_format(
                int(from_year.group(1)),
                int(from_month.group(1))
            )
            
            # Process end date
            end_date = self._convert_to_fiscal_format(
                int(to_year.group(1)),
                int(to_month.group(1))
            )
            
            return {
                'start_date': start_date,
                'end_date': end_date,
                'fiscal_year_start': self.fiscal_year_start_month
            }
            
        except Exception as e:
            logger.error(f"Failed to parse email time range: {str(e)}")
            return None
