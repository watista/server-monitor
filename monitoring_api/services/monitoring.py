import os
import psutil
import requests
import subprocess
from config import config
from services.logger import logger
from services.models import (
    IPStatus,
    DiskStatus,
    AptUpdateStatus,
    LoadStatus,
    MemoryStatus
)

def check_ip() -> IPStatus:
    """Check if public IP matches expected value."""
    try:
        response = requests.get("https://api4.ipify.org?format=json")
        logger.debug(f"IP Check response: {response}")
        ip = response.json().get("ip")

        if ip and ip != config.thresholds["ip_check"]:
            logger.warning(f"IP Mismatch! Current: {ip}, Expected: {config.thresholds['ip_check']}")
            return IPStatus(success=False, message=f"IP changed to {ip}")

        return IPStatus(success=True, message="IP is stable")

    except Exception as e:
        logger.error(f"Failed to check IP: {e}")
        return IPStatus(success=False, message="IP check failed")


def check_disk() -> DiskStatus:
    """Check if disk space is below threshold."""
    alerts = []

    for disk in config.monitored_disks:
        disk = disk.strip()
        if not os.path.ismount(disk):
            logger.warning(f"Skipping non-existent or unmounted disk: {disk}")
            continue

        usage = psutil.disk_usage(disk)
        if usage.percent > (100 - config.thresholds["disk_space_threshold"]):
            alerts.append(f"Low disk space on {disk} ({usage.percent}% used)")

    return DiskStatus(success=(not alerts), message=alerts or "All monitored disks have sufficient space")


def check_apt_updates() -> AptUpdateStatus:
    """Check for available APT package updates and count critical security updates."""
    try:
        # Run command to check for upgradable packages
        result = subprocess.run(["apt", "list", "--upgradable"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")[1:]  # Skip first line (header)

        total_updates = len(lines)
        critical_updates = sum(1 for line in lines if "security" in line.lower())

        logger.info(f"APT Updates: {total_updates} total, {critical_updates} critical")
        return AptUpdateStatus(total_updates=total_updates, critical_updates=critical_updates)

    except Exception as e:
        logger.error(f"Failed to check APT updates: {e}")
        return AptUpdateStatus(total_updates=-1, critical_updates=-1)


def check_load() -> LoadStatus:
    """Check system load averages for the past 1, 5, and 15 minutes."""
    try:
        load_1m, load_5m, load_15m = os.getloadavg()

        logger.info(f"Load Averages - 1m: {load_1m}, 5m: {load_5m}, 15m: {load_15m}")
        return LoadStatus(load_1m=load_1m, load_5m=load_5m, load_15m=load_15m)

    except Exception as e:
        logger.error(f"Failed to check system load: {e}")
        return LoadStatus(load_1m=-1, load_5m=-1, load_15m=-1)

def check_memory() -> MemoryStatus:
    """Check available RAM and Swap memory."""
    try:
        ram = psutil.virtual_memory()
        swap = psutil.swap_memory()

        available_ram = ram.available / (1024 ** 2)
        total_ram = ram.total / (1024 ** 2)
        available_swap = swap.free / (1024 ** 2)
        total_swap = swap.total / (1024 ** 2)

        logger.info(f"Memory Check - RAM: {available_ram:.2f}/{total_ram:.2f} MB, Swap: {available_swap:.2f}/{total_swap:.2f} MB")
        return MemoryStatus(
            available_ram=available_ram,
            total_ram=total_ram,
            available_swap=available_swap,
            total_swap=total_swap
        )

    except Exception as e:
        logger.error(f"Failed to check memory: {e}")
        return MemoryStatus(available_ram=-1, total_ram=-1, available_swap=-1, total_swap=-1)
