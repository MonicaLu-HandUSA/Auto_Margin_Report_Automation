import os
import time
from typing import Optional, Dict, Tuple
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select
from urllib.parse import urlencode

from config import Config

DOWNLOAD_DIR = os.path.abspath(os.path.join(os.getcwd(), "temp_downloads"))


def ensure_download_dir() -> str:
	os.makedirs(DOWNLOAD_DIR, exist_ok=True)
	return DOWNLOAD_DIR


class NetSuiteRPADownloader:
	def __init__(self, headless: bool = True):
		self.headless = headless
		self.driver = None

	def _init_driver(self):
		ensure_download_dir()
		options = ChromeOptions()
		if self.headless:
			options.add_argument("--headless=new")
		options.add_argument("--disable-gpu")
		options.add_argument("--window-size=1920,1080")
		prefs = {
			"download.default_directory": DOWNLOAD_DIR,
			"download.prompt_for_download": False,
			"download.directory_upgrade": True,
			"safebrowsing.enabled": True,
		}
		options.add_experimental_option("prefs", prefs)
		self.driver = webdriver.Chrome(options=options)

	def _build_quarter_url(self, saved_search_id: str, start: date, end: date) -> str:
		params = {
			"script": Config.NETSUITE_SCRIPT_ID,
			"deploy": Config.NETSUITE_DEPLOY_ID,
			"whence": "",
			"saved_search_id": saved_search_id,
			"start_date": start.strftime("%Y-%m-%d"),
			"end_date": end.strftime("%Y-%m-%d"),
		}
		return f"{Config.NETSUITE_URL}?{urlencode(params)}"

	def login(self, start_url: Optional[str] = None):
		if not self.driver:
			self._init_driver()
		d = self.driver
		# Navigate either to a target page (preferred) or the base URL; NetSuite will redirect to login.
		d.get(start_url or Config.NETSUITE_URL)
		self._attempt_login()

	def _is_login_page(self) -> bool:
		try:
			# Look for any reasonable email field on the page
			d = self.driver
			email_selectors = [
				"input[type='email']",
				"#email",
				"input[name='email']",
				"input[aria-label='Email address']",
				"input[placeholder*='Email']",
			]
			for sel in email_selectors:
				if d.find_elements(By.CSS_SELECTOR, sel):
					return True
			return False
		except Exception:
			return False

	def _attempt_login(self):
		"""Fill the Oracle NetSuite login form like the one in the screenshot and submit."""
		d = self.driver
		wait = WebDriverWait(d, 30)
		if not self._is_login_page():
			return
		# Try multiple selectors to be robust across themes
		email_selectors = [
			(By.CSS_SELECTOR, "input[type='email']"),
			(By.ID, "email"),
			(By.CSS_SELECTOR, "input[name='email']"),
			(By.CSS_SELECTOR, "input[aria-label='Email address']"),
			(By.CSS_SELECTOR, "input[placeholder*='Email']"),
		]
		pwd_selectors = [
			(By.CSS_SELECTOR, "input[type='password']"),
			(By.ID, "password"),
			(By.CSS_SELECTOR, "input[name='password']"),
			(By.CSS_SELECTOR, "input[aria-label='Password']"),
		]
		btn_selectors = [
			(By.CSS_SELECTOR, "button[type='submit']"),
			(By.ID, "submitButton"),
			(By.CSS_SELECTOR, "input[type='submit']"),
		]
		# Fill email
		email_input = None
		for by, sel in email_selectors:
			try:
				email_input = wait.until(EC.presence_of_element_located((by, sel)))
				break
			except TimeoutException:
				continue
		if not email_input:
			raise RuntimeError("Login page email field not found")
		email_input.clear()
		email_input.send_keys(Config.NETSUITE_USERNAME)
		# Fill password
		pwd_input = None
		for by, sel in pwd_selectors:
			try:
				pwd_input = wait.until(EC.presence_of_element_located((by, sel)))
				break
			except TimeoutException:
				continue
		if not pwd_input:
			raise RuntimeError("Login page password field not found")
		pwd_input.clear()
		pwd_input.send_keys(Config.NETSUITE_PASSWORD or "")
		# Click Log In
		login_btn = None
		for by, sel in btn_selectors:
			try:
				login_btn = wait.until(EC.element_to_be_clickable((by, sel)))
				break
			except TimeoutException:
				continue
		if not login_btn:
			raise RuntimeError("Login page submit button not found")
		login_btn.click()
		# Allow redirect
		try:
			wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
		except TimeoutException:
			pass

	def _handle_security_questions(self):
		"""Handle NetSuite security questions during login."""
		try:
			# Check if we're on the security question page
			def on_security_page() -> bool:
				if "securityquestions" in (self.driver.current_url or ""):
					return True
				try:
					self.driver.find_element(By.XPATH, "//input[@type='text' or @type='password']")
					self.driver.find_element(By.XPATH, "//button[contains(., 'Submit')] | //input[@type='submit']")
					return True
				except Exception:
					return False

			# Wait for security page
			try:
				WebDriverWait(self.driver, 5).until(lambda d: on_security_page())
			except Exception:
				return  # No security question present

			# Get page text and find matching question
			page_text = self.driver.find_element(By.TAG_NAME, "body").text.strip()
			matched_answer = None
			matched_question = None

			for question, answer in Config.SECURITY_QA.items():
				if question.lower() in page_text.lower():
					matched_answer = answer
					matched_question = question
					print(f"Matched security question: {question}")
					break

			if not matched_answer:
				print(f"Security question not recognized. Page text: {page_text[:80]}...")
				return

			# Find and fill answer input
			inputs = self.driver.find_elements(By.XPATH, "//input[@type='text' or @type='password']")
			target = next((el for el in inputs if el.is_displayed() and el.is_enabled()), None)
			
			if not target:
				print("Could not locate answer input field")
				return

			target.clear()
			target.send_keys(matched_answer)

			# Submit answer
			try:
				submit = self.driver.find_element(By.XPATH, "//button[contains(., 'Submit')] | //input[@type='submit']")
				submit.click()
			except Exception as e:
				print(f"Could not find submit button: {str(e)}")
				return

			# Wait for redirect
			try:
				WebDriverWait(self.driver, 30).until(
					lambda d: "securityquestions" not in (d.current_url or "")
				)
			except Exception:
				pass

			print("Security question answered successfully")

		except Exception as e:
			print(f"Error handling security questions: {str(e)}")
			self.driver.save_screenshot("security_question_error.png")
			raise

	def _handle_download_page(self, start_date: str, end_date: str):
		"""
		Handle the margin report download page by setting dates and triggering download
		
		Args:
			start_date: Date string in format "FY YYYY : QX YYYY : MMM YYYY"
			end_date: Date string in format "FY YYYY : QX YYYY : MMM YYYY"
		"""
		try:
			# Wait for subsidiary dropdown and select Baby Trend
			subsidiary_dropdown = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.XPATH, "//select[contains(@id, 'subsidiary')]"))
			)
			Select(subsidiary_dropdown).select_by_visible_text("Baby Trend")

			# Set Period From date
			period_from = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.XPATH, "//select[contains(@id, 'periodfrom')]"))
			)
			Select(period_from).select_by_visible_text(start_date)

			# Set Period To date
			period_to = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.XPATH, "//select[contains(@id, 'periodto')]"))
			)
			Select(period_to).select_by_visible_text(end_date)

			# Click Download button
			download_button = WebDriverWait(self.driver, 10).until(
				EC.element_to_be_clickable((By.XPATH, "//input[@value='Download'] | //button[contains(text(), 'Download')]"))
			)
			download_button.click()

			# Wait for download to complete
			time.sleep(5)  # Adjust timeout as needed
			
			print(f"Successfully initiated download for period {start_date} to {end_date}")

		except Exception as e:
			print(f"Error handling download page: {str(e)}")
			self.driver.save_screenshot("download_page_error.png")
			raise

		return True

	def _select_dates_and_download(self, start_date: Dict[str, str], end_date: Dict[str, str]):
		"""
		Select dates from NetSuite dropdowns and trigger download
		
		Args:
			start_date: Dictionary containing netsuite_dropdown_value for period from
			end_date: Dictionary containing netsuite_dropdown_value for period to
		"""
		
		try:
			# Wait for subsidiary dropdown and select Baby Trend
			subsidiary_dropdown = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.XPATH, "//select[contains(@id, 'subsidiary')]"))
			)
			Select(subsidiary_dropdown).select_by_visible_text("Baby Trend")

			# Select Period From
			period_from = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.XPATH, "//select[contains(@id, 'periodfrom')]"))
			)
			Select(period_from).select_by_visible_text(start_date['netsuite_dropdown_value'])

			# Select Period To
			period_to = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.XPATH, "//select[contains(@id, 'periodto')]"))
			)
			Select(period_to).select_by_visible_text(end_date['netsuite_dropdown_value'])

			# Click Download button
			download_button = WebDriverWait(self.driver, 10).until(
				EC.element_to_be_clickable((By.XPATH, "//input[@value='Download'] | //button[contains(text(), 'Download')]"))
			)
			download_button.click()

			# Wait for download to complete
			time.sleep(5)  # Adjust timeout as needed 
			return True
		
		except Exception as e:
			print(f"Error selecting dates and downloading: {str(e)}")
			self.driver.save_screenshot("download_error.png")
			return False

	def download_quarter(self, saved_search_id: str, year: int, quarter: int, start: date, end: date) -> Optional[str]:
		if not self.driver:
			self._init_driver()
		d = self.driver
		url = self._build_quarter_url(saved_search_id, start, end)
		d.get(url)
		# If redirected to login, perform login then navigate back to the target URL
		if self._is_login_page():
			self._attempt_login()
			# Re-open the target after login
			d.get(url)
		wait = WebDriverWait(d, 30)
		# Trigger export; selectors must match your scriptlet page
		try:
			export_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#export, a#export")))
			export_button.click()
			# Wait for file to appear in download dir
			filename = f"margin_{year}_Q{quarter}.xls"
			outfile = os.path.join(DOWNLOAD_DIR, filename)
			deadline = time.time() + 60
			while time.time() < deadline:
				for f in os.listdir(DOWNLOAD_DIR):
					if f.lower().endswith((".xls", ".xlsx")):
						candidate = os.path.join(DOWNLOAD_DIR, f)
						# rename to standard name
						os.replace(candidate, outfile)
						return outfile
				time.sleep(1)
			raise TimeoutException("Export did not complete in time")
		except Exception as e:
			return None

	def close(self):
		if self.driver:
			self.driver.quit()
			self.driver = None
