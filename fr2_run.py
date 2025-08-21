#!/usr/bin/env python3
import argparse
import logging
import os
from datetime import datetime, date
from typing import List, Tuple

from quarter_utils import enumerate_quarters
from rpa_downloader import NetSuiteRPADownloader

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("fr2")


def parse_date(s: str) -> date:
	return datetime.strptime(s, "%Y-%m-%d").date()


def main():
	parser = argparse.ArgumentParser(description="FR-2: Automated Report Extraction via RPA")
	parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
	parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
	parser.add_argument("--saved_search_id", required=True, help="NetSuite Saved Search ID")
	parser.add_argument("--headless", action="store_true", help="Run browser headless")
	args = parser.parse_args()

	start = parse_date(args.start)
	end = parse_date(args.end)
	quarters = enumerate_quarters(start, end)
	logger.info("Quarters to process: %s", [(y, q) for y, q, _ in quarters])

	downloader = NetSuiteRPADownloader(headless=args.headless)
	failed = []
	try:
		logger.info("Logging into NetSuite")
		downloader.login()
		for year, quarter, (qs, qe) in quarters:
			logger.info("Processing %d Q%d (%s to %s)", year, quarter, qs, qe)
			outfile = downloader.download_quarter(args.saved_search_id, year, quarter, qs, qe)
			if outfile:
				logger.info("Saved: %s", outfile)
			else:
				logger.error("Failed: %d Q%d", year, quarter)
				failed.append((year, quarter))
	finally:
		downloader.close()

	if failed:
		logger.warning("Partial success. Failed quarters: %s", failed)
		raise SystemExit(2)
	else:
		logger.info("All quarters processed successfully")


if __name__ == "__main__":
	main()
