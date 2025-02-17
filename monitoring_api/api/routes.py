#!/usr/bin/python3

from fastapi import APIRouter, Depends, FastAPI, Request
from auth import get_current_user_api_key
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

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Server Monitoring API is running"}


@router.get("/all_status", response_model=MonitoringStatus)
async def get_status(user: dict = Depends(get_current_user_api_key)):
    """Return all system status in structured format."""

    checks = MonitoringStatus(
        public_ip=check_ip(),
        disk_space=check_disk(),
        apt_updates=check_apt_updates(),
        load_status=check_load(),
        memory_status=check_memory(),
        logged_in_user_status=check_logged_in_users(),
        process_status=check_processes()
    )

    logger.info(f"User {user['username']} requested all system status")
    return checks


@router.get("/ip_check", response_model=IPStatus)
async def get_ip(user: dict = Depends(get_current_user_api_key)):
    """Return ip check in structured format."""
    logger.info(f"User {user['username']} requested IP check")
    return check_ip()


@router.get("/disk_check", response_model=DiskSpaceStatus)
async def get_disk(user: dict = Depends(get_current_user_api_key)):
    """Return disk check in structured format."""
    logger.info(f"User {user['username']} requested disk check")
    return check_disk()


@router.get("/apt_check", response_model=AptUpdateStatus)
async def get_apt(user: dict = Depends(get_current_user_api_key)):
    """Return disk check in structured format."""
    logger.info(f"User {user['username']} requested APT check")
    return check_apt_updates()


@router.get("/load_check", response_model=LoadStatus)
async def get_load(user: dict = Depends(get_current_user_api_key)):
    """Return system load status."""
    logger.info(f"User {user['username']} requested load status")
    return check_load()


@router.get("/memory_check", response_model=MemoryStatus)
async def get_memory(user: dict = Depends(get_current_user_api_key)):
    """Return system memory status."""
    logger.info(f"User {user['username']} requested memory status")
    return check_memory()


@router.get("/users_check", response_model=LoggedInUsersStatus)
async def get_logged_in_users_status(user: dict = Depends(get_current_user_api_key)):
    """Return the number of logged-in users."""
    logger.info(f"User {user['username']} requested logged-in user status")
    return check_logged_in_users()


@router.get("/processes_check", response_model=ProcessStatus)
async def get_process_status(user: dict = Depends(get_current_user_api_key)):
    """Return process status for monitored processes."""
    logger.info(f"User {user['username']} requested process status")
    return check_processes()
