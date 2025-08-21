import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
	"""Configuration class for NetSuite and application settings"""
	
	# NetSuite Configuration
	NETSUITE_URL = "https://837809-sb1.app.netsuite.com/app/site/hosting/scriptlet.nl"
	NETSUITE_SCRIPT_ID = "1574"
	NETSUITE_DEPLOY_ID = "1"
	
	# NetSuite Credentials (loaded from environment variables)
	NETSUITE_USERNAME = os.getenv("NETSUITE_USERNAME", "bill.li@hand-usa.com")
	NETSUITE_PASSWORD = os.getenv("NETSUITE_PASSWORD")
	# Security questions (optional for RPA flow)
	NS_SQ_1 = os.getenv("NS_SQ_1", "mochi")
	NS_SQ_2 = os.getenv("NS_SQ_2", "boston")
	NS_SQ_3 = os.getenv("NS_SQ_3", "sanjose")
	
	# Fiscal Calendar Configuration
	FISCAL_YEAR_START_MONTH = 1  # January (1-based)
	
	# Email Configuration
	EMAIL_SUBJECT_PATTERN = "Margin Report"
	
	# Logging Configuration
	LOG_LEVEL = "INFO"
	LOG_FILE = "margin_report_automation.log"
	
	@classmethod
	def validate_config(cls):
		"""Validate that all required configuration is present"""
		if not cls.NETSUITE_PASSWORD:
			raise ValueError("NETSUITE_PASSWORD environment variable is required")
		return True
