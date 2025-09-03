from datetime import date, timedelta
from typing import List, Tuple, Dict

class QuarterCalculator:
    def __init__(self, fiscal_year_start_month: int = 1):
        self.fiscal_year_start_month = fiscal_year_start_month
        
    def get_quarter(self, month: int) -> int:
        """Calculate quarter based on fiscal year start month"""
        if not (1 <= month <= 12):
            raise ValueError("month must be 1..12")
        months_since_fiscal_start = (month - self.fiscal_year_start_month) % 12
        return (months_since_fiscal_start // 3) + 1
    
    def get_fiscal_year(self, calendar_year: int, month: int) -> int:
        """Calculate fiscal year based on calendar date"""
        if month < self.fiscal_year_start_month:
            return calendar_year
        return calendar_year + 1
    
    def quarter_start_end(self, fiscal_year: int, quarter: int) -> Tuple[date, date]:
        """Get start and end dates for a fiscal quarter"""
        if not (1 <= quarter <= 4):
            raise ValueError("quarter must be 1..4")
            
        # Calculate the month offset for this quarter
        quarter_month_start = self.fiscal_year_start_month + ((quarter - 1) * 3)
        if quarter_month_start > 12:
            quarter_month_start -= 12
            fiscal_year += 1
            
        # Calculate end month
        quarter_month_end = quarter_month_start + 2
        end_year = fiscal_year
        if quarter_month_end > 12:
            quarter_month_end -= 12
            end_year += 1
            
        start = date(fiscal_year, quarter_month_start, 1)
        # Calculate last day of end month
        if quarter_month_end in [4, 6, 9, 11]:
            end_day = 30
        elif quarter_month_end == 2:
            if end_year % 4 == 0 and (end_year % 100 != 0 or end_year % 400 == 0):
                end_day = 29
            else:
                end_day = 28
        else:
            end_day = 31
            
        end = date(end_year, quarter_month_end, end_day)
        return start, end


def enumerate_quarters(self, start_date: date, end_date: date) -> List[Tuple[int,int,Tuple[date,date]]]:
    """
    Get list of fiscal quarters between two dates
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        List of tuples (fiscal_year, quarter, (quarter_start_date, quarter_end_date))
    """
    if start_date > end_date:
        raise ValueError("start_date must be <= end_date")
        
    quarters = []
    current_year = self.get_fiscal_year(start_date.year, start_date.month)
    current_quarter = self.get_quarter(start_date.month)
    
    while True:
        qs, qe = self.quarter_start_end(current_year, current_quarter)
        # Intersect with requested range
        range_start = max(qs, start_date)
        range_end = min(qe, end_date)
        
        if range_start <= range_end:
            quarters.append((current_year, current_quarter, (qs, qe)))
            
        # Advance to next quarter
        if current_quarter == 4:
            current_quarter = 1
            current_year += 1
        else:
            current_quarter += 1
            
        # Check if we've passed the end date
        if qs > end_date:
            break
            
        # Safety stop
        if len(quarters) > 40:
            break
            
    return quarters
