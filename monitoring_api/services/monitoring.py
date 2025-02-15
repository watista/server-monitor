import os
import psutil
import requests
from config import config
from services.logger import logger
from services.models import IPStatus, DiskStatus

def check_ip():
    """Check if public IP matches expected value."""
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        ip = response.json().get("ip")

        if ip and ip != config.thresholds["ip_check"]:
            logger.warning(f"IP Mismatch! Current: {ip}, Expected: {config.thresholds['ip_check']}")
            return IPStatus(success=False, message=f"IP changed to {ip}")

        IPStatus(success=True, message="IP is stable")

    except Exception as e:
        logger.error(f"Failed to check IP: {e}")
        return IPStatus(success=False, message="IP check failed")


def check_disk():
    """Check if disk space is below threshold."""
    alerts = []
    for partition in psutil.disk_partitions():
        usage = psutil.disk_usage(partition.mountpoint)
        if usage.percent > (100 - config.thresholds["disk_space_threshold"]):
            alerts.append(f"Low disk space on {partition.mountpoint} ({usage.percent}% used)")

    return DiskStatus(success=(not alerts), message=alerts or "Disk space is fine")

# Other checks (APT updates, load, memory, logged-in users, services) follow a similar pattern...
