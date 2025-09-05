#!/usr/bin/env python3
import argparse
import json
from email_processor import EmailProcessor


def main():
    parser = argparse.ArgumentParser(description="Parse email content and print fiscal parameters")
    parser.add_argument("--subject", default="Margin Report", help="Email subject (default: 'Margin Report')")
    parser.add_argument("--body", required=True, help="Email body text containing fiscal start month and date range")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    ep = EmailProcessor()
    result = ep.process_email(args.subject, args.body)
    if not result:
        print("Error: could not parse fiscal parameters from email.")
        print("Email body should contain:")
        print("- Fiscal Year Starts From Which Month: MM")
        print("- Period From(Year): YYYY")
        print("- Period From(Month): MM")
        print("- Period To(Year): YYYY")
        print("- Period To(Month): MM")
        return

    output = {
        "email_subject": result["email_subject"],
        "fiscal_summary": result["fiscal_summary"],
        "start_date": result["start_date"],
        "end_date": result["end_date"],
        "fiscal_year_start": result["time_range"]["fiscal_year_start"]
    }
    if args.pretty:
        print(json.dumps(output, indent=2))
    else:
        print(json.dumps(output))


if __name__ == "__main__":
	main()
