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
        parser.add_argument("-v", "--verbose",
                            action="store_true", help="Enable console logging")
        parser.add_argument("-e", "--env", type=str,
                            choices=["dev", "live"], help="Set env mode (default: dev)")
        parser.add_argument("-E", "--env-path", type=str,
                            help="Location of the env file (default: .env)")
        parser.add_argument("-i", "--chat-id", type=int,
                            help="User or group ID of the Telegram chat (default: 0)")
        parser.add_argument("-a", "--allowed-users", type=str,
                            help="Single or multiple Telegram IDs, seperated by a comma, for usage restriction (default: 0)")
        parser.add_argument("-l", "--log-dir", type=str,
                            help="Directory for log files (default: /var/log/server-monitor-bot)")
        parser.add_argument("-f", "--log-filename", type=str,
                            help="Log filename (default: app.log)")
        parser.add_argument("-L", "--log-level", type=str, choices=[
                            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Log level (default: INFO)")
        parser.add_argument("-t", "--bot-token", type=str,
                            help="Live bot token (default: change-this-token)")
        parser.add_argument("-T", "--bot-token-dev", type=str,
                            help="Dev bot token (default: change-this-token)")
        parser.add_argument("-b", "--api-address", type=str,
                            help="Url of the monitoring API (default: 0.0.0.0)")
        parser.add_argument("-p", "--api-port", type=int,
                            help="Port of the monitoring API (default: 8000)")
        parser.add_argument("-u", "--api-user", type=str,
                            help="User for the monitoring API (default: admin)")
        parser.add_argument("-P", "--api-password", type=str,
                            help="Password for the monitoring API (default: change-this-password)")
        parser.add_argument("-q", "--ip-threshold", type=str,
                            help="IP to check (default: 0.0.0.0)")
        parser.add_argument("-A", "--apt-threshold", type=int,
                            help="APT packages threshold (default: 10)")
        parser.add_argument("-s", "--apt-security-threshold", type=int,
                            help="APT security packages threshold (default: 1)")
        parser.add_argument("-d", "--disk-threshold", type=float,
                            help="Free disk space threshold (default: 5)")
        parser.add_argument("-x", "--load-1-threshold",
                            type=float, help="1 min load threshold (default: 5)")
        parser.add_argument("-y", "--load-5-threshold",
                            type=float, help="5 min load threshold (default: 3)")
        parser.add_argument("-z", "--load-15-threshold",
                            type=float, help="15 min load threshold (default: 2)")
        parser.add_argument("-r", "--ram-threshold", type=float,
                            help="Free RAM threshold (default: 25)")
        parser.add_argument("-S", "--swap-threshold", type=float,
                            help="Free swap threshold (default: 25)")
        parser.add_argument("-U", "--users-threshold", type=int,
                            help="Logged in users threshold (default: 2)")
        parser.add_argument("-m", "--alert-interval", type=int,
                            help="Interval for alerts te be send in seconds (default: 300)")
        parser.add_argument("-n", "--server-name", type=str,
                            help="Name of the monitor server (default: server-name)")
        parser.add_argument("-R", "--log-retention", type=int,
                            help="Log retention days, for the privacy policy (default: 30)")
        parser.add_argument("-B", "--bot-owner", type=int,
                            help="Bot owner username, for the privacy policy (default: owner)")
        args = parser.parse_args()

        # Load .env file
        dotenv_path = Path(args.env_path) if args.env_path else Path(".env")
        load_dotenv(dotenv_path=dotenv_path)

        # Function to prioritize CLI args > .env > default
        def get_env_var(arg_value: str, env_var: str, default_value: str):
            return arg_value if arg_value is not None else os.getenv(env_var, default_value)

        # Assign values (CLI args > .env > Defaults)
        self.verbose = args.verbose
        self.env = get_env_var(args.env, "ENV", "dev")
        self.env_path = get_env_var(args.env_path, "ENV_PATH", ".env")
        self.chat_id = get_env_var(args.env_path, "CHAT_ID", "0")
        self.allowed_users = get_env_var(
            args.allowed_users, "ALLOWED_USERS", "0")
        self.log_dir = get_env_var(
            args.log_dir, "LOG_DIR", "/var/log/server-monitor-bot")
        self.log_filename = get_env_var(
            args.log_filename, "LOG_FILENAME", "app.log")
        self.log_level = get_env_var(args.log_level, "LOG_LEVEL", "INFO")
        self.bot_token = get_env_var(
            args.bot_token, "BOT_TOKEN", "change-this-token")
        self.bot_token_dev = get_env_var(
            args.bot_token_dev, "BOT_TOKEN_DEV", "change-this-token")
        self.api_address = get_env_var(
            args.api_address, "API_ADDRESS", "0.0.0.0")
        self.api_port = get_env_var(args.api_port, "API_PORT", 8000)
        self.api_user = get_env_var(args.api_user, "API_USER", "admin")
        self.api_password = get_env_var(
            args.api_password, "API_PASSWORD", "change-this-password")
        self.ip_threshold = get_env_var(
            args.ip_threshold, "IP_THRESHOLD", "0.0.0.0")
        self.apt_threshold = get_env_var(
            args.apt_threshold, "APT_THRESHOLD", "10")
        self.apt_security_threshold = get_env_var(
            args.apt_security_threshold, "APT_SECURITY_THRESHOLD", "1")
        self.disk_threshold = get_env_var(
            args.disk_threshold, "DISK_THRESHOLD", "5")
        self.load_1_threshold = get_env_var(
            args.load_1_threshold, "LOAD_1_THRESHOLD", "5")
        self.load_5_threshold = get_env_var(
            args.load_5_threshold, "LOAD_5_THRESHOLD", "3")
        self.load_15_threshold = get_env_var(
            args.load_15_threshold, "LOAD_15_THRESHOLD", "2")
        self.ram_threshold = get_env_var(
            args.ram_threshold, "RAM_THRESHOLD", "25")
        self.swap_threshold = get_env_var(
            args.swap_threshold, "SWAP_THRESHOLD", "25")
        self.users_threshold = get_env_var(
            args.users_threshold, "USERS_THRESHOLD", "2")
        self.alert_interval = get_env_var(
            args.alert_interval, "ALERT_INTERVAL", "300")
        self.server_name = get_env_var(
            args.server_name, "SERVER_NAME", "server-name")
        self.log_retention = get_env_var(
            args.log_retention, "LOG_RETENTION", "30")
        self.bot_owner = get_env_var(args.bot_owner, "BOT_OWNER", "owner")


# Global instance of Config
config = Config()
