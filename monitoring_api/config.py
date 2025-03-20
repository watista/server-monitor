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
        parser = argparse.ArgumentParser(description="Server Monitor API")
        parser.add_argument("-v", "--verbose",
                            action="store_true", help="Enable console logging")
        parser.add_argument("-e", "--env-path", type=str,
                            help="Path to the env file (default: .env)")
        parser.add_argument("-l", "--log-dir", type=str,
                            help="Directory for log files (default: /var/log/server-monitor-api)")
        parser.add_argument("-f", "--log-filename", type=str, help="Log filename (default: app.log)")
        parser.add_argument("-L", "--log-level", type=str, choices=[
                            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Log level (default: INFO)")
        parser.add_argument("-i", "--host-ip", type=str,
                            help="API server IP address (default: 0.0.0.0)")
        parser.add_argument("-p", "--host-port", type=int, help="API server port (default: 8000)")
        parser.add_argument("-d", "--monitored-disks", type=str,
                            help="Comma-separated list of monitored disks (default: /)")
        parser.add_argument("-P", "--monitored-processes", type=str,
                            help="Comma-separated list of monitored processes (default: )")
        parser.add_argument("-s", "--oauth-secret-key", type=str,
                            help="The secret key to encode JWT tokens (default: change-this-secret-key)")
        parser.add_argument("-a", "--oauth-algorithm", type=str,
                            help="OAuth2 algorithm to encode JWT tokens (default: HS256)")
        parser.add_argument("-t", "--oauth-token-expire", type=int,
                            help="Time in minutes the OAuth2 token expires (default: 60)")
        parser.add_argument("-r", "--api-rate-limit", type=int,
                            help="Maximum request per second (default: 5)")
        parser.add_argument("-F", "--failed-attempt-limit", type=int,
                            help="Max failed attempts before blocking token request (default: 5)")
        parser.add_argument("-b", "--block-time-minutes", type=int,
                            help="Block duration in minutes (default: 10)")
        parser.add_argument("-D", "--db-name", type=str, help="Name of the database (default: users.db)")
        parser.add_argument("--add-users", action="store_true",
                            help="Add a new user to the database")
        parser.add_argument("--db-username", type=str,
                            help="Username for the new user")
        parser.add_argument("--db-password", type=str,
                            help="Password for the new user")
        args = parser.parse_args()

        # Load .env file
        dotenv_path = Path(args.env_path) if args.env_path else Path(".env")
        load_dotenv(dotenv_path=dotenv_path)

        # Function to prioritize CLI args > .env > default
        def get_env_var(arg_value, env_var, default_value):
            return arg_value if arg_value is not None else os.getenv(env_var, default_value)

        # Assign values (CLI > .env > Defaults)
        self.verbose = args.verbose
        self.env_path = get_env_var(args.env_path, "ENV_PATH", ".env")
        self.log_dir = get_env_var(args.log_dir, "LOG_DIR", "/var/log/server-monitor-api")
        self.log_filename = get_env_var(
            args.log_filename, "LOG_FILENAME", "app.log")
        self.log_level = get_env_var(args.log_level, "LOG_LEVEL", "INFO")
        self.host_ip = get_env_var(args.host_ip, "HOST_IP", "0.0.0.0")
        self.host_port = get_env_var(args.host_port, "HOST_PORT", 8000)
        self.monitored_disks = get_env_var(
            args.monitored_disks, "MONITORED_DISKS", "/").split(",")
        self.monitored_processes = get_env_var(
            args.monitored_processes, "MONITORED_PROCESSES", "").split(",")
        self.oauth_secret_key = get_env_var(
            args.oauth_secret_key, "OAUTH_SECRET_KEY", "change-this-secret-key")
        self.oauth_algorithm = get_env_var(
            args.oauth_algorithm, "OAUTH_ALGORITHM", "HS256")
        self.oauth_token_expire = get_env_var(
            args.oauth_token_expire, "OAUTH_TOKEN_EXPIRE", 60)
        self.api_rate_limit = get_env_var(
            args.api_rate_limit, "API_RATE_LIMIT", 5)
        self.failed_attempt_limit = get_env_var(
            args.failed_attempt_limit, "FAILED_ATTEMPT_LIMIT", 5)
        self.block_time_minutes = get_env_var(
            args.block_time_minutes, "BLOCK_TIME_MINUTES", 10)
        self.db_name = get_env_var(args.db_name, "DB_NAME", "users.db")
        self.add_users = args.add_users
        self.db_username = args.db_username
        self.db_password = args.db_password


# Global instance of Config
config = Config()
