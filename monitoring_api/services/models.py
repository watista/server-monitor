from pydantic import BaseModel
from typing import Dict, List, Union

class IPStatus(BaseModel):
    success: bool
    message: str

class DiskStatus(BaseModel):
    success: bool
    message: Union[str, List[str]]

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

class MonitoringStatus(BaseModel):
    public_ip: IPStatus
    disk_space: DiskStatus
    apt_updates: AptUpdateStatus
    load_status: LoadStatus
    memory_status: MemoryStatus
