from datetime import date, timedelta
from typing import List, Tuple, Dict

MONTH_TO_Q = {1:1,2:1,3:1,4:2,5:2,6:2,7:3,8:3,9:3,10:4,11:4,12:4}


def get_quarter(month: int) -> int:
	if not (1 <= month <= 12):
		raise ValueError("month must be 1..12")
	return MONTH_TO_Q[month]


def quarter_start_end(year: int, quarter: int) -> Tuple[date, date]:
	if quarter == 1:
		start = date(year, 1, 1)
		end = date(year, 3, 31)
	elif quarter == 2:
		start = date(year, 4, 1)
		end = date(year, 6, 30)
	elif quarter == 3:
		start = date(year, 7, 1)
		end = date(year, 9, 30)
	elif quarter == 4:
		start = date(year, 10, 1)
		end = date(year, 12, 31)
	else:
		raise ValueError("quarter must be 1..4")
	return start, end


def enumerate_quarters(start_date: date, end_date: date) -> List[Tuple[int,int,Tuple[date,date]]]:
	if start_date > end_date:
		raise ValueError("start_date must be <= end_date")
	quarters = []
	current_year = start_date.year
	current_quarter = get_quarter(start_date.month)
	while True:
		qs, qe = quarter_start_end(current_year, current_quarter)
		# intersect with requested range
		range_start = max(qs, start_date)
		range_end = min(qe, end_date)
		if range_start <= range_end:
			quarters.append((current_year, current_quarter, (qs, qe)))
		# advance
		if current_quarter == 4:
			current_quarter = 1
			current_year += 1
		else:
			current_quarter += 1
		if date(current_year, 1, 1) > end_date and current_quarter == 1:
			break
		# safety stop
		if len(quarters) > 40:
			break
	# filter fully outside range just in case
	result = []
	for y, q, (qs, qe) in quarters:
		if qe < start_date or qs > end_date:
			continue
		result.append((y, q, (qs, qe)))
	return result
