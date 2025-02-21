#!/usr/bin/python3

import os
import sqlite3
import bcrypt
from typing import Optional, Dict, Any
from config import config
from services.logger import logger

DB_FILE: str = config.db_name


def init_db() -> None:
    """Check if database exists; if not, create users table."""
    try:
        if not os.path.exists(DB_FILE):
            logger.info("Database not found, creating new database...")
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        hashed_password TEXT NOT NULL
                    )
                """)
                conn.commit()
            logger.info("Database and users table created successfully.")
    except sqlite3.OperationalError as e:
        logger.error(f"SQLite error during database initialization: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected error during database initialization")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    try:
        if not password:
            logger.error("Attempted to hash an empty password")
            raise ValueError("Password cannot be empty")
        hash_pwd = bcrypt.hashpw(password.encode(
            "utf-8"), bcrypt.gensalt()).decode("utf-8")
        logger.info("Successfully hashed a password")
        return hash_pwd
    except Exception as e:
        logger.exception("Error hashing password")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed version."""
    try:
        if not plain_password or not hashed_password:
            logger.error("Password verification failed due to missing input")
            return False
        ver_pwd = bcrypt.checkpw(plain_password.encode(
            "utf-8"), hashed_password.encode("utf-8"))
        logger.info("Successfully verified a password")
        return ver_pwd
    except Exception as e:
        logger.exception("Error verifying password")
        return False


def add_user(username: str, password: str) -> None:
    """Add a new user to the database with a hashed password."""
    try:
        hashed_pwd = hash_password(password)
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, hashed_password) VALUES (?, ?)", (username, hashed_pwd))
            conn.commit()
        logger.info(f"User '{username}' added successfully!")
    except sqlite3.IntegrityError:
        logger.warning(f"User '{username}' already exists.")
    except Exception as e:
        logger.error(f"Error adding user '{username}': {str(e)}")


def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Retrieve user information from the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, hashed_password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        return {"username": user[0], "hashed_password": user[1]} if user else None
    except Exception as e:
        logger.error(f"Error retrieving user '{username}': {str(e)}")
        return None


# Ensure database is initialized when module is imported
init_db()
