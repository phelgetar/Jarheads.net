#!/usr/bin/env python3
"""
Secure Configuration Manager for Marine Corps News Aggregator
Loads configuration from environment variables with fallback to .env file
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class ConfigManager:
    """
    Centralized configuration management with secure credential handling.

    Usage:
        from src.utils.config_manager import config

        api_key = config.api_key
        db_path = config.database_path
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure single config instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Find project root and load .env
        self.project_root = Path(__file__).parent.parent.parent
        env_path = self.project_root / '.env'

        # Load .env file if it exists
        if env_path.exists():
            load_dotenv(env_path)

        self._initialized = True

    # =========================================================================
    # WordPress API Configuration
    # =========================================================================

    @property
    def api_url(self) -> str:
        """WordPress API base URL"""
        return os.getenv('JARHEADS_API_URL', 'https://jarheads.net')

    @property
    def api_key(self) -> Optional[str]:
        """WordPress API key - returns None if not configured"""
        key = os.getenv('JARHEADS_API_KEY')
        if key and key != 'your-wordpress-api-key-here':
            return key
        return None

    @property
    def has_api_credentials(self) -> bool:
        """Check if API credentials are properly configured"""
        return self.api_key is not None

    # =========================================================================
    # Email Configuration
    # =========================================================================

    @property
    def smtp_server(self) -> str:
        """SMTP server address"""
        return os.getenv('SMTP_SERVER', 'smtp.gmail.com')

    @property
    def smtp_port(self) -> int:
        """SMTP server port"""
        return int(os.getenv('SMTP_PORT', '587'))

    @property
    def sender_email(self) -> Optional[str]:
        """Sender email address"""
        email = os.getenv('SENDER_EMAIL')
        if email and email != 'your-email@gmail.com':
            return email
        return None

    @property
    def sender_password(self) -> Optional[str]:
        """Sender email password/app password"""
        password = os.getenv('SENDER_PASSWORD')
        if password and password != 'your-app-password-here':
            return password
        return None

    @property
    def receiver_email(self) -> str:
        """Receiver email address for notifications"""
        return os.getenv('RECEIVER_EMAIL', 'admin@jarheads.net')

    @property
    def has_email_credentials(self) -> bool:
        """Check if email credentials are properly configured"""
        return self.sender_email is not None and self.sender_password is not None

    # =========================================================================
    # Database Configuration
    # =========================================================================

    @property
    def database_path(self) -> Path:
        """Path to SQLite database"""
        db_path = os.getenv('DATABASE_PATH', 'data/marine_corps_news.db')
        # Make path absolute if relative
        path = Path(db_path)
        if not path.is_absolute():
            path = self.project_root / path
        return path

    @property
    def data_dir(self) -> Path:
        """Data directory path"""
        return self.database_path.parent

    # =========================================================================
    # Ahrefs API Configuration
    # =========================================================================

    @property
    def ahrefs_api_key(self) -> Optional[str]:
        """Ahrefs API key for SEO data"""
        key = os.getenv('AHREFS_API_KEY')
        if key and key != 'your-ahrefs-api-key-here':
            return key
        return None

    @property
    def has_ahrefs_credentials(self) -> bool:
        """Check if Ahrefs credentials are configured"""
        return self.ahrefs_api_key is not None

    # =========================================================================
    # Logging Configuration
    # =========================================================================

    @property
    def log_level(self) -> str:
        """Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"""
        return os.getenv('LOG_LEVEL', 'INFO').upper()

    @property
    def log_dir(self) -> Path:
        """Log directory path"""
        log_dir = os.getenv('LOG_DIR', 'logs')
        path = Path(log_dir)
        if not path.is_absolute():
            path = self.project_root / path
        return path

    # =========================================================================
    # Crawling Configuration
    # =========================================================================

    @property
    def max_workers(self) -> int:
        """Maximum number of parallel workers for crawling"""
        return int(os.getenv('MAX_WORKERS', '5'))

    @property
    def crawl_delay(self) -> float:
        """Delay between requests in seconds"""
        return float(os.getenv('CRAWL_DELAY_SECONDS', '1'))

    @property
    def request_timeout(self) -> int:
        """HTTP request timeout in seconds"""
        return int(os.getenv('REQUEST_TIMEOUT_SECONDS', '30'))

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def validate(self) -> dict:
        """
        Validate configuration and return status for each component.

        Returns:
            dict with component names as keys and (bool, message) tuples as values
        """
        results = {}

        # Database
        if self.database_path.exists():
            results['database'] = (True, f"Found at {self.database_path}")
        else:
            results['database'] = (False, f"Not found at {self.database_path}")

        # WordPress API
        if self.has_api_credentials:
            results['wordpress_api'] = (True, "Credentials configured")
        else:
            results['wordpress_api'] = (False, "API key not configured")

        # Email
        if self.has_email_credentials:
            results['email'] = (True, "Credentials configured")
        else:
            results['email'] = (False, "Email credentials not configured")

        # Ahrefs
        if self.has_ahrefs_credentials:
            results['ahrefs'] = (True, "API key configured")
        else:
            results['ahrefs'] = (False, "API key not configured")

        # Log directory
        if self.log_dir.exists():
            results['logging'] = (True, f"Log directory exists at {self.log_dir}")
        else:
            results['logging'] = (False, f"Log directory not found at {self.log_dir}")

        return results

    def print_status(self):
        """Print configuration status to console"""
        print("=" * 60)
        print("Configuration Status")
        print("=" * 60)

        validation = self.validate()
        for component, (status, message) in validation.items():
            icon = "[OK]" if status else "[--]"
            print(f"{icon} {component.replace('_', ' ').title()}: {message}")

        print("=" * 60)


# Singleton instance for easy import
config = ConfigManager()


if __name__ == "__main__":
    # Test configuration when run directly
    config.print_status()
