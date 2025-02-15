from pydantic import BaseModel
from typing import Dict, List, Union

class IPStatus(BaseModel):
    success: bool
    message: str

class DiskStatus(BaseModel):
    success: bool
    message: Union[str, List[str]]

class MonitoringStatus(BaseModel):
    public_ip: IPStatus
    disk_space: DiskStatus
