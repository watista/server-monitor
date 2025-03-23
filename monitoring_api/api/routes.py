#!/usr/bin/python3

import traceback
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Dict
from auth import authenticate_user, create_access_token, get_current_user
from services.monitoring import (
    check_ip,
    check_disk,
    check_apt_updates,
    check_load,
    check_memory,
    check_logged_in_users,
    check_processes
)
from services.models import (
    MonitoringStatus,
    IPStatus,
    DiskSpaceStatus,
    AptUpdateStatus,
    LoadStatus,
    MemoryStatus,
    LoggedInUsersStatus,
    ProcessStatus
)
from config import config
from services.logger import logger

# Create default value
rate_limit = f"{str(config.api_rate_limit)}/second"

# Init router with rate limiter
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom 429 Error Response"""
    logger.warning(f"Rate limit exceeded: {request.client.host} for {request.url}")
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests, slow down!"}
    )


@router.get("/")
async def root() -> Dict[str, str]:
    """Default root path"""
    logger.info(f"User requested root path")
    return {"message": "Server Monitoring API is running"}


@router.post("/auth/token")
@limiter.limit(rate_limit)
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    """Authenticate user and return a JWT access token."""
    logger.info(f"Login attempt for user: {form_data.username}")

    try:
        # Authenticate user
        user = authenticate_user(form_data.username, form_data.password)

        # Create access token
        access_token_expires = timedelta(minutes=config.oauth_token_expire)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires)

        logger.info(f"User {user['username']} logged in successfully (Token expires in {config.oauth_token_expire} minutes)")
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException as e:
        # Log specific authentication failures
        logger.warning(f"Failed login attempt for user: {form_data.username} - Reason: {e.detail}")
        raise e

    except Exception as e:
        # Log unexpected errors with full traceback
        logger.error(f"Unexpected error during login attempt for user: {form_data.username} - Error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status/all", response_model=MonitoringStatus, dependencies=[Depends(get_current_user)])
@limiter.limit(rate_limit)
async def get_status(request: Request, user: dict = Depends(get_current_user)) -> MonitoringStatus:
    """Return all system status in structured format."""

    checks = MonitoringStatus(
        public_ip=await check_ip(),
        disk_space=await check_disk(),
        apt_updates=await check_apt_updates(),
        load_status=await check_load(),
        memory_status=await check_memory(),
        logged_in_user_status=await check_logged_in_users(),
        process_status=await check_processes()
    )

    logger.info(f"User {user['username']} requested all system status")
    return checks


@router.get("/status/ip", response_model=IPStatus, dependencies=[Depends(get_current_user)])
@limiter.limit(rate_limit)
async def get_ip(request: Request, user: dict = Depends(get_current_user)) -> IPStatus:
    """Return ip check in structured format."""
    logger.info(f"User {user['username']} requested IP check")
    return await check_ip()


@router.get("/status/disk", response_model=DiskSpaceStatus, dependencies=[Depends(get_current_user)])
@limiter.limit(rate_limit)
async def get_disk(request: Request, user: dict = Depends(get_current_user)) -> DiskSpaceStatus:
    """Return disk check in structured format."""
    logger.info(f"User {user['username']} requested disk check")
    return await check_disk()


@router.get("/status/apt", response_model=AptUpdateStatus, dependencies=[Depends(get_current_user)])
@limiter.limit(rate_limit)
async def get_apt(request: Request, user: dict = Depends(get_current_user)) -> AptUpdateStatus:
    """Return disk check in structured format."""
    logger.info(f"User {user['username']} requested APT check")
    return await check_apt_updates()


@router.get("/status/load", response_model=LoadStatus, dependencies=[Depends(get_current_user)])
@limiter.limit(rate_limit)
async def get_load(request: Request, user: dict = Depends(get_current_user)) -> LoadStatus:
    """Return system load status."""
    logger.info(f"User {user['username']} requested load status")
    return await check_load()


@router.get("/status/memory", response_model=MemoryStatus, dependencies=[Depends(get_current_user)])
@limiter.limit(rate_limit)
async def get_memory(request: Request, user: dict = Depends(get_current_user)) -> MemoryStatus:
    """Return system memory status."""
    logger.info(f"User {user['username']} requested memory status")
    return await check_memory()


@router.get("/status/users", response_model=LoggedInUsersStatus, dependencies=[Depends(get_current_user)])
@limiter.limit(rate_limit)
async def get_logged_in_users_status(request: Request, user: dict = Depends(get_current_user)) -> LoggedInUsersStatus:
    """Return the number of logged-in users."""
    logger.info(f"User {user['username']} requested logged-in user status")
    return await check_logged_in_users()


@router.get("/status/processes", response_model=ProcessStatus, dependencies=[Depends(get_current_user)])
@limiter.limit(rate_limit)
async def get_process_status(request: Request, user: dict = Depends(get_current_user)) -> ProcessStatus:
    """Return process status for monitored processes."""
    logger.info(f"User {user['username']} requested process status")
    return await check_processes()
