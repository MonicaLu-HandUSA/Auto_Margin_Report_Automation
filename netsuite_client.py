import requests
import logging
from typing import Dict, Optional, Any
from config import Config
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

class NetSuiteClient:
    """Client for interacting with NetSuite API"""
    
    def __init__(self):
        """Initialize NetSuite client with configuration"""
        self.base_url = Config.NETSUITE_URL
        self.script_id = Config.NETSUITE_SCRIPT_ID
        self.deploy_id = Config.NETSUITE_DEPLOY_ID
        self.username = Config.NETSUITE_USERNAME
        self.password = Config.NETSUITE_PASSWORD
        self.security_question = Config.NETSUITE_SECURITY_QUESTION
        
        # Initialize encryption key for sensitive data
        self._init_encryption()
        
        # Validate configuration
        self._validate_config()
    
    def _init_encryption(self):
        """Initialize encryption for sensitive data"""
        try:
            # Generate a key for encryption (in production, this should be stored securely)
            key = Fernet.generate_key()
            self.cipher_suite = Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {str(e)}")
            self.cipher_suite = None
    
    def _validate_config(self):
        """Validate NetSuite configuration"""
        if not self.password:
            raise ValueError("NetSuite password is required")
        if not self.security_question:
            raise ValueError("NetSuite security question is required")
        
        logger.info("NetSuite configuration validated successfully")
    
    def _encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not self.cipher_suite:
            return data
        
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.warning(f"Failed to encrypt data: {str(e)}")
            return data
    
    def _decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not self.cipher_suite:
            return encrypted_data
        
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.warning(f"Failed to decrypt data: {str(e)}")
            return encrypted_data
    
    def authenticate(self) -> bool:
        """
        Authenticate with NetSuite
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # In a real implementation, this would handle NetSuite's authentication flow
            # including security questions and session management
            
            auth_data = {
                'username': self.username,
                'password': self._decrypt_sensitive_data(self.password),
                'security_question': self._decrypt_sensitive_data(self.security_question)
            }
            
            # Log authentication attempt (without sensitive data)
            logger.info(f"Attempting to authenticate with NetSuite as {self.username}")
            
            # For demonstration purposes, we'll simulate successful authentication
            # In production, this would make actual API calls to NetSuite
            logger.info("NetSuite authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"NetSuite authentication failed: {str(e)}")
            return False
    
    def construct_query_url(self, fiscal_params: Dict[str, str], saved_search_id: str = None) -> str:
        """
        Construct NetSuite query URL with fiscal parameters
        
        Args:
            fiscal_params: Dictionary with fiscal parameters
            saved_search_id: Optional saved search ID
            
        Returns:
            Constructed NetSuite URL
        """
        try:
            # Build query parameters
            params = {
                'script': self.script_id,
                'deploy': self.deploy_id,
                'whence': '',
                'fiscal_year': fiscal_params.get('fiscal_year', ''),
                'quarter': fiscal_params.get('quarter', ''),
                'month': fiscal_params.get('month', ''),
                'year': fiscal_params.get('year', ''),
                'quarter_num': fiscal_params.get('quarter_num', ''),
                'month_num': fiscal_params.get('month_num', '')
            }
            
            # Add saved search ID if provided
            if saved_search_id:
                params['saved_search_id'] = saved_search_id
            
            # Construct URL
            query_string = '&'.join([f"{k}={v}" for k, v in params.items() if v])
            url = f"{self.base_url}?{query_string}"
            
            logger.info(f"Constructed NetSuite query URL: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to construct query URL: {str(e)}")
            raise
    
    def execute_query(self, fiscal_params: Dict[str, str], saved_search_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Execute NetSuite query with fiscal parameters
        
        Args:
            fiscal_params: Dictionary with fiscal parameters
            saved_search_id: Optional saved search ID
            
        Returns:
            Query results or None if execution fails
        """
        try:
            # Authenticate first
            if not self.authenticate():
                logger.error("Authentication failed, cannot execute query")
                return None
            
            # Construct query URL
            query_url = self.construct_query_url(fiscal_params, saved_search_id)
            
            # Execute query (in production, this would make actual HTTP requests)
            logger.info(f"Executing NetSuite query: {query_url}")
            
            # For demonstration, return mock results
            # In production, this would return actual NetSuite data
            mock_results = {
                'query_url': query_url,
                'fiscal_params': fiscal_params,
                'saved_search_id': saved_search_id,
                'status': 'success',
                'data': f"Mock data for {fiscal_params.get('fiscal_year', 'Unknown')} - {fiscal_params.get('quarter', 'Unknown')}"
            }
            
            logger.info("NetSuite query executed successfully")
            return mock_results
            
        except Exception as e:
            logger.error(f"Failed to execute NetSuite query: {str(e)}")
            return None
    
    def get_fiscal_summary(self, fiscal_params: Dict[str, str]) -> str:
        """
        Get formatted fiscal summary for display
        
        Args:
            fiscal_params: Dictionary with fiscal parameters
            
        Returns:
            Formatted fiscal summary string
        """
        try:
            fiscal_year = fiscal_params.get('fiscal_year', 'Unknown')
            quarter = fiscal_params.get('quarter', 'Unknown')
            month = fiscal_params.get('month', 'Unknown')
            
            return f"{fiscal_year} : {quarter} : {month}"
            
        except Exception as e:
            logger.error(f"Failed to create fiscal summary: {str(e)}")
            return "Error creating fiscal summary"
