#!/usr/bin/env python3
import argparse
import json
from email_processor import EmailProcessor


def main():
	parser = argparse.ArgumentParser(description="Parse email content and print fiscal parameters")
	parser.add_argument("--subject", default="Margin Report", help="Email subject (default: 'Margin Report')")
	parser.add_argument("--body", required=True, help="Email body text containing time range, e.g. 'time range 08/2024 - 08/2025'")
	parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
	args = parser.parse_args()

	ep = EmailProcessor()
	result = ep.process_email(args.subject, args.body)
	if not result:
		print("Error: could not parse fiscal parameters from email. Ensure subject contains 'Margin Report' and body has a time range like '08/2024 - 08/2025'.")
		return

	output = {
		"email_subject": result["email_subject"],
		"fiscal_summary": result["fiscal_summary"],
		"start_date": result["start_date"],
		"end_date": result["end_date"],
	}
	if args.pretty:
		print(json.dumps(output, indent=2))
	else:
		print(json.dumps(output))


if __name__ == "__main__":
	main()
