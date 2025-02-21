#!/usr/bin/python3

import time
from cachetools import TTLCache
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from config import config
from typing import Dict, Optional, Any
from services.logger import logger
from services.db import get_user, verify_password

# Get some config values
SECRET_KEY = config.oauth_secret_key
ALGORITHM = config.oauth_algorithm
FAILED_ATTEMPT_LIMIT = config.failed_attempt_limit
BLOCK_TIME_MINUTES = config.block_time_minutes
failed_login_cache = TTLCache(maxsize=1000, ttl=BLOCK_TIME_MINUTES * 60)

# OAuth2 & API Key security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def is_user_blocked(username: str) -> bool:
    """Check if a user is temporarily blocked."""
    block_time = failed_login_cache.get(username)

    if isinstance(block_time, (int, float)) and block_time > time.time():
        remaining_time = int(block_time - time.time())
        logger.warning(f"User {username} is temporarily blocked ({remaining_time} seconds remaining)")
        return True

    return False


def register_failed_login(username: str) -> None:
    """Register a failed login attempt and block if limit exceeded."""
    try:
        attempts = failed_login_cache.get(username, 0) + 1

        if attempts >= FAILED_ATTEMPT_LIMIT:
            failed_login_cache[username] = time.time() + \
                (BLOCK_TIME_MINUTES * 60)
            logger.warning(f"User {username} blocked for {BLOCK_TIME_MINUTES} minutes due to excessive failed logins")
        else:
            failed_login_cache[username] = attempts
            logger.warning(f"Failed login attempt {attempts}/{FAILED_ATTEMPT_LIMIT} for user: {username}")
    except Exception as e:
        logger.error(f"Error tracking failed login for user {username}: {str(e)}")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT access token."""
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=config.oauth_token_expire))
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Created access token for user {data.get('sub')} (expires: {expire})")
        return token
    except Exception as e:
        logger.error(f"Error generating access token: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def verify_access_token(token: str) -> Dict[str, str]:
    """Verify JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            logger.warning(
                "Token verification failed: No username found in payload")
            raise HTTPException(status_code=401, detail="Invalid token")

        logger.info(f"Token verified successfully for user: {username}")
        return {"username": username}

    except JWTError as e:
        logger.warning(f"Invalid token attempt: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        logger.error(f"Unexpected error verifying token: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def authenticate_user(username: str, password: str) -> Dict[str, str]:
    """Authenticate user based on username & password."""
    user = get_user(username)

    try:
        if not user:
            logger.warning(f"Login failed for non-existent user: {username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if is_user_blocked(username):
            raise HTTPException(status_code=403, detail=f"Too many failed attempts. Try again in {BLOCK_TIME_MINUTES} minutes")

        if not verify_password(password, user["hashed_password"]):
            logger.warning(f"Invalid password attempt for user: {username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Reset failed attempts after successful login
        if username in failed_login_cache:
            del failed_login_cache[username]

        logger.info(f"User {username} authenticated successfully")
        return {"username": username}

    except HTTPException as e:
        logger.warning(f"Authentication failed for user {username}: {e.detail}")
        raise e

    except Exception as e:
        logger.error(f"Unexpected error during authentication for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """Get the current user from the OAuth2 bearer token."""
    logger.info("Received authentication request using OAuth2 token")

    try:
        user = verify_access_token(token)

        if not user or "username" not in user:
            logger.warning(
                "Authentication failed: Token valid but no user data found")
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials")

        logger.info(f"Authenticated user: {user['username']}")
        return user

    except JWTError as e:
        logger.warning(f"Invalid token attempt: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

    except HTTPException as e:
        logger.warning(f"Authentication failed: {e.detail}")
        raise e

    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
