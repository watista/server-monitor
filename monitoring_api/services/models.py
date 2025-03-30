#!/usr/bin/python3

from pydantic import BaseModel
from typing import Dict, List, Any


class IPStatus(BaseModel):
    ip: str


class DiskSpaceStatus(BaseModel):
    disks: Dict[str, float]


class AptUpdateStatus(BaseModel):
    total_updates: int
    critical_updates: int


class LoadStatus(BaseModel):
    load_1m: float
    load_5m: float
    load_15m: float


class MemoryStatus(BaseModel):
    available_ram: float
    total_ram: float
    available_swap: float
    total_swap: float


class LoggedInUsersStatus(BaseModel):
    user_count: int
    usernames: List[str]


class ProcessStatus(BaseModel):
    processes: Dict[str, bool]


class PlexStatus(BaseModel):
    plex: Dict[str, Any]


class MonitoringStatus(BaseModel):
    public_ip: IPStatus
    disk_space: DiskSpaceStatus
    apt_updates: AptUpdateStatus
    load_status: LoadStatus
    memory_status: MemoryStatus
    logged_in_user_status: LoggedInUsersStatus
    process_status: ProcessStatus
