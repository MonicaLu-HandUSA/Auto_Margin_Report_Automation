import os
import win32com.client
import logging
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)

class ReportDelivery:
    def __init__(self, original_sender: str):
        self.original_sender = original_sender
        self.max_retries = 2

    def send_email(self, subject: str, body: str, attachment_path: Optional[str] = None) -> bool:
        """Send email using Outlook"""
        retries = 0
        while retries <= self.max_retries:
            try:
                outlook = win32com.client.Dispatch('Outlook.Application')
                mail = outlook.CreateItem(0)
                mail.To = self.original_sender
                mail.Subject = subject
                mail.Body = body
                
                if attachment_path and os.path.exists(attachment_path):
                    mail.Attachments.Add(attachment_path)
                
                mail.Send()
                logger.info(f"Successfully sent email to {self.original_sender}")
                return True
                
            except Exception as e:
                retries += 1
                logger.error(f"Attempt {retries}: Failed to send email: {str(e)}")
                if retries > self.max_retries:
                    self._escalate_error(f"Failed to send email after {self.max_retries} attempts")
                    return False
        
        return False

    def copy_to_shared_folder(self, file_path: str) -> bool:
        """Copy report to shared folder"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Source file not found: {file_path}")
                
            filename = os.path.basename(file_path)
            dest_path = os.path.join(Config.SHARED_FOLDER_PATH, filename)
            
            # Create shared folder if it doesn't exist
            os.makedirs(Config.SHARED_FOLDER_PATH, exist_ok=True)
            
            # Copy file
            import shutil
            shutil.copy2(file_path, dest_path)
            
            logger.info(f"Successfully copied report to shared folder: {dest_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy file to shared folder: {str(e)}")
            self._escalate_error("Failed to copy file to shared folder")
            return False

    def send_success_notification(self, report_path: str):
        """Send success notification email"""
        subject = "Margin Report Generation Successful"
        body = f"""
The margin report has been successfully generated and processed.
Report period: {os.path.basename(report_path)}

The report is attached to this email and has also been saved to the shared folder.
"""
        self.send_email(subject, body, report_path)

    def send_failure_notification(self, error_message: str):
        """Send failure notification email"""
        subject = "Margin Report Generation Failed"
        body = f"""
The margin report generation process has encountered an error:

{error_message}

Please review the error and retry the process if necessary.
"""
        self.send_email(subject, body)

    def _escalate_error(self, error_message: str):
        """Escalate error to IT team"""
        subject = "ALERT: Margin Report Automation Error"
        body = f"""
Critical error in margin report automation:

{error_message}

Please investigate and resolve this issue.

System Details:
- Time: {datetime.now()}
- Original Requestor: {self.original_sender}
"""
        # Send to IT team
        outlook = win32com.client.Dispatch('Outlook.Application')
        mail = outlook.CreateItem(0)
        mail.To = Config.IT_TEAM_EMAIL
        mail.Subject = subject
        mail.Body = body
        mail.Importance = 2  # High importance
        mail.Send()
        
        logger.error(f"Error escalated to IT team: {error_message}")
