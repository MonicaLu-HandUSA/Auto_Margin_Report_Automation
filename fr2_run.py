import argparse
import logging
from datetime import datetime, date

from quarter_utils import enumerate_quarters
from rpa_downloader import NetSuiteRPADownloader
from config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
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

    # Build login/start URL from config
    start_url = (
        f"{Config.NETSUITE_URL}"
        f"?script={Config.NETSUITE_SCRIPT_ID}"
        f"&deploy={Config.NETSUITE_DEPLOY_ID}"
        f"&whence="
    )

    downloader = NetSuiteRPADownloader(headless=args.headless)
    failed = []

    try:
        # Step 1: Login with explicit start_url
        logger.info("Logging into NetSuite")
        downloader.login(start_url=start_url)
        logger.info("Now at: %s", downloader.driver.current_url)

        # Step 2: Handle security questions
        try:
            downloader._handle_security_questions()
            logger.info("Security question handled successfully")
        except Exception as e:
            logger.error("Error handling security question: %s", e)
            raise

        # Step 3: Process each quarter
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

