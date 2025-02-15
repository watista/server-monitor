#!/usr/bin/python3

import argparse
from pathlib import Path
import os
from dotenv import load_dotenv

class Config:
    """Singleton class to store configuration settings."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Parse CLI arguments and load environment variables."""
        parser = argparse.ArgumentParser(description="Server Monitor API")
        parser.add_argument("-v", "--verbose", action="store_true",
                            help="Enable console logging")
        parser.add_argument("-e", "--env", help="Environment value: live / dev", required=True)
        args = parser.parse_args()

        # Validate environment
        if args.env not in ["live", "dev"]:
            parser.error("Invalid --env/-e value. Must be 'live' or 'dev'.")

        # Store args as attributes
        self.verbose = args.verbose
        self.env = args.env

        # Load .env file based on environment
        dotenv_path = Path("/root/scripts/file-monitor/dot-env") if self.env == "live" else Path("dot-env")
        load_dotenv(dotenv_path=dotenv_path)

        # Validate required env vars
        required_vars = ["API_KEY_ADMIN", "API_KEY_USER", "LOG_DIR", "LOG_FILENAME", "LOG_TYPE", "HOST_IP", "HOST_PORT"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

        self.api_keys = {
            "admin": os.getenv("API_KEY_ADMIN"),
            "user": os.getenv("API_KEY_USER"),
        }

        self.thresholds = {
            "ip_check": "77.165.252.248",
            "max_apt_updates": 10,
            "critical_updates": 1,
            "disk_space_threshold": 2,  # in %
            "memory_threshold": 25,  # in %
            "load_1m": 30,
            "load_5m": 20,
            "load_15m": 10,
            "max_logged_users": 2,
        }

        self.log_dir = os.getenv("LOG_DIR")
        self.log_filename = os.getenv("LOG_FILENAME")
        self.log_type = os.getenv("LOG_TYPE")
        self.host_ip = os.getenv("HOST_IP")
        self.host_port = os.getenv("HOST_PORT")

    def get(self, key, default=None):
        """Get an environment variable or config setting."""
        return getattr(self, key, os.getenv(key, default))

# Global instance of Config
config = Config()

# Import logger AFTER config is fully initialized
from services.logger import get_logger
logger = get_logger()
