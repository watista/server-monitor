from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from config import config
from services.logger import logger

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def get_current_user_api_key(api_key: str = Security(api_key_header)):
    """Authenticate user based on API key."""
    if not api_key or api_key not in config.api_keys.values():
        logger.warning("Unauthorized API access attempt.")
        raise HTTPException(status_code=401, detail="Invalid API key")

    username = next((user for user, key in config.api_keys.items() if key == api_key), "Unknown")
    logger.info(f"Authenticated API access by user: {username}")
    return {"username": username}
