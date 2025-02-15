#!/usr/bin/python3

from fastapi import APIRouter, Depends, FastAPI, Request
from auth import get_current_user_api_key
from services.monitoring import check_ip, check_disk
from services.models import MonitoringStatus
from config import config
from services.logger import logger

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Server Monitoring API is running"}


@router.get("/status")
async def get_status(user: dict = Depends(get_current_user_api_key)):
    """Return system status in structured format."""

    checks = MonitoringStatus(
        public_ip=check_ip(),
        disk_space=check_disk(),
    )

    logger.info(f"User {user['username']} requested system status")
    return checks
