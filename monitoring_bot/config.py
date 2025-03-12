#!/usr/bin/python3

import argparse
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Singleton class to store configuration settings."""
    _instance: Optional["Config"] = None

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """Parse CLI arguments and load environment variables."""
        parser = argparse.ArgumentParser(description="Server Monitor Bot")
        parser.add_argument("-v", "--verbose", action="store_true", help="Enable console logging")
        parser.add_argument("-e", "--env", type=str, choices=["dev", "live"], help="Set env mode")
        parser.add_argument("--env-path", type=str, help="Location of the env file")
        parser.add_argument("--log-dir", type=str, help="Directory for log files")
        parser.add_argument("--log-filename", type=str, help="Log filename")
        parser.add_argument("--log-level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Log level")
        parser.add_argument("--bot-token", type=str, help="Live bot token")
        parser.add_argument("--bot-token-dev", type=str, help="Dev bot token")
        parser.add_argument("--api-address", type=str, help="Url of the monitoring API")
        parser.add_argument("--api-port", type=str, help="Port of the monitoring API")
        parser.add_argument("--api-user", type=str, help="User for the monitoring API")
        parser.add_argument("--api-password", type=str, help="Password for the monitoring API")
        parser.add_argument("--ip-threshold", type=str, help="IP to check")
        parser.add_argument("--apt-threshold", type=str, help="APT packages threshold")
        parser.add_argument("--apt-security-threshold", type=str, help="APT security packages threshold")
        parser.add_argument("--disk-threshold", type=str, help="Free disk space threshold")
        parser.add_argument("--load-1-threshold", type=str, help="1 min load threshold")
        parser.add_argument("--load-5-threshold", type=str, help="5 min load threshold")
        parser.add_argument("--load-15-threshold", type=str, help="15 min load threshold")
        parser.add_argument("--ram-threshold", type=str, help="Free RAM threshold")
        parser.add_argument("--swap-threshold", type=str, help="Free swap threshold")
        parser.add_argument("--users-threshold", type=str, help="Logged in users threshold")
        parser.add_argument("--alert-interval", type=str, help="Interval for alerts te be send in minutes")
        args = parser.parse_args()

        # Load .env file
        dotenv_path = Path(args.env_path) if args.env_path else Path(".env")
        load_dotenv(dotenv_path=dotenv_path)

        # Function to prioritize CLI args > .env > default
        def get_env_var(arg_value, env_var, default_value):
            return arg_value if arg_value is not None else os.getenv(env_var, default_value)

        # Assign values (CLI > .env > Defaults)
        self.verbose = args.verbose
        self.env = get_env_var(args.env, "ENV", "dev")
        self.env_path = get_env_var(args.env_path, "ENV_PATH", ".env")
        self.log_dir = get_env_var(args.log_dir, "LOG_DIR", "/var/log/server-monitor-bot")
        self.log_filename = get_env_var(args.log_filename, "LOG_FILENAME", "app.log")
        self.log_level = get_env_var(args.log_level, "LOG_LEVEL", "INFO")
        self.bot_token = get_env_var(args.bot_token, "BOT_TOKEN", "change-this-token")
        self.bot_token_dev = get_env_var(args.bot_token_dev, "BOT_TOKEN_DEV", "change-this-token")
        self.api_address = get_env_var(args.api_address, "API_ADDRESS", "0.0.0.0")
        self.api_port = get_env_var(args.api_port, "API_PORT", 8000)
        self.api_user = get_env_var(args.api_user, "API_USER", "admin")
        self.api_password = get_env_var(args.api_password, "API_PASSWORD", "change-this-password")
        self.ip_threshold = get_env_var(args.ip_threshold, "IP_THRESHOLD", "0.0.0.0")
        self.apt_threshold = get_env_var(args.apt_threshold, "APT_THRESHOLD", "10")
        self.apt_security_threshold = get_env_var(args.apt_security_threshold, "1", "0.0.0.0")
        self.disk_threshold = get_env_var(args.disk_threshold, "DISK_THRESHOLD", "5")
        self.load_1_threshold = get_env_var(args.load_1_threshold, "LOAD_1_THRESHOLD", "5")
        self.load_5_threshold = get_env_var(args.load_5_threshold, "LOAD_5_THRESHOLD", "3")
        self.load_15_threshold = get_env_var(args.load_15_threshold, "LOAD_15_THRESHOLD", "2")
        self.ram_threshold = get_env_var(args.ram_threshold, "RAM_THRESHOLD", "25")
        self.swap_threshold = get_env_var(args.swap_threshold, "SWAP_THRESHOLD", "25")
        self.users_threshold = get_env_var(args.users_threshold, "USERS_THRESHOLD", "2")
        self.alert_interval = get_env_var(args.alert_interval, "ALERT_INTERVAL", "5")


# Global instance of Config
config = Config()
