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
        Convert year and month to NetSuite fiscal format
        
        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)
            
        Returns:
            Dictionary with fiscal parameters
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
            
            result = {
                'fiscal_year': f"FY {fiscal_year}",
                'quarter': f"Q{quarter} {fiscal_year}",
                'month': f"{month_abbr} {fiscal_year}",
                'year': str(fiscal_year),
                'quarter_num': str(quarter),
                'month_num': f"{month:02d}",
                'original_year': str(year),
                'original_month': str(month)
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
        """Calculate quarter based on month"""
        if month <= 3:
            return 1
        elif month <= 6:
            return 2
        elif month <= 9:
            return 3
        else:
            return 4
    
    def _get_month_abbreviation(self, month: int) -> str:
        """Get month abbreviation (e.g., 1 -> Jan)"""
        month_names = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        return month_names[month - 1]
    
    def parse_email_time_range(self, email_body: str) -> Optional[Dict[str, Dict[str, str]]]:
        """
        Parse time range from email body (e.g., "08/2024 - 08/2025")
        
        Args:
            email_body: Email body text
            
        Returns:
            Dictionary with start and end date fiscal parameters
        """
        try:
            # Look for time range pattern
            time_range_pattern = r'(\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{4})'
            match = re.search(time_range_pattern, email_body)
            
            if match:
                start_date = match.group(1)
                end_date = match.group(2)
                
                start_params = self.parse_date_string(start_date)
                end_params = self.parse_date_string(end_date)
                
                if start_params and end_params:
                    return {
                        'start_date': start_params,
                        'end_date': end_params
                    }
            
            logger.warning(f"No valid time range found in email body: {email_body}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse email time range: {str(e)}")
            return None
