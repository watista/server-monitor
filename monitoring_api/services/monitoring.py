#!/usr/bin/python3

import os
import psutil
import aiohttp
import subprocess
from config import config
from services.logger import logger
from services.models import (
    IPStatus,
    DiskSpaceStatus,
    AptUpdateStatus,
    LoadStatus,
    MemoryStatus,
    LoggedInUsersStatus,
    ProcessStatus
)


async def check_ip() -> IPStatus:
    """Return the value of the current public IP."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api4.ipify.org?format=json") as response:
                if not response.ok:
                    logger.error(f"Not OK response for IPv4 GET. Error: {response.status_code} - {response.reason} - {response.text}")
                    return IPStatus(ip="-1")
                logger.info(f"IP Check response: {response.text}")
                ip_response = await response.json()
                ip = ip_response.get("ip")
                return IPStatus(ip=str(ip))

    except Exception as e:
        logger.error(f"Failed to check IP: {e}")
        return IPStatus(ip="-1")


async def check_disk() -> DiskSpaceStatus:
    """Return a dictionary of monitored disks and their free space percentage."""
    disk_info = {}

    try:
        for disk in config.monitored_disks:
            disk = disk.strip()
            if not os.path.ismount(disk):
                logger.warning(f"Skipping non-existent or unmounted disk: {disk}")
                continue

            usage = psutil.disk_usage(disk)
            free_percentage = 100 - usage.percent
            disk_info[disk] = free_percentage

        return DiskSpaceStatus(disks=disk_info)

    except Exception as e:
        logger.error(f"Failed to check disks: {e}")
        return DiskSpaceStatus(disks={"error": -1})


async def check_apt_updates() -> AptUpdateStatus:
    """Check for available APT package updates and count critical security updates."""
    try:
        # Run command to check for upgradable packages
        result = subprocess.run(
            ["apt", "list", "--upgradable"], capture_output=True, text=True)

        # Skip first line (header)
        lines = result.stdout.strip().split("\n")[1:]
        total_updates = len(lines)
        critical_updates = sum(
            1 for line in lines if "security" in line.lower())
        logger.info(f"APT Updates: {total_updates} total, {critical_updates} critical")
        return AptUpdateStatus(total_updates=total_updates, critical_updates=critical_updates)

    except Exception as e:
        logger.error(f"Failed to check APT updates: {e}")
        return AptUpdateStatus(total_updates=-1, critical_updates=-1)


async def check_load() -> LoadStatus:
    """Check system load averages for the past 1, 5, and 15 minutes."""
    try:
        load_1m, load_5m, load_15m = os.getloadavg()
        logger.info(f"Load Averages - 1m: {load_1m}, 5m: {load_5m}, 15m: {load_15m}")
        return LoadStatus(load_1m=load_1m, load_5m=load_5m, load_15m=load_15m)

    except Exception as e:
        logger.error(f"Failed to check system load: {e}")
        return LoadStatus(load_1m=-1, load_5m=-1, load_15m=-1)


async def check_memory() -> MemoryStatus:
    """Check available RAM and Swap memory."""
    try:
        ram = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Calculate ram/swap in MB
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


async def check_logged_in_users() -> LoggedInUsersStatus:
    """Check the number of users currently logged into the system."""
    try:
        users = psutil.users()
        usernames = list(set(user.name for user in users))
        user_count = len(usernames)

        logger.info(f"Logged-in Users: {user_count} - {usernames}")
        return LoggedInUsersStatus(user_count=user_count, usernames=usernames)

    except Exception as e:
        logger.error(f"Failed to check logged-in users: {e}")
        return LoggedInUsersStatus(user_count=-1, usernames=[])


async def check_processes() -> ProcessStatus:
    """Check if the specified processes from ENV are running."""
    process_status = {
        proc.strip(): False for proc in config.monitored_processes if proc.strip()}

    try:
        running_processes = {p.info["name"].lower()
                             for p in psutil.process_iter(attrs=["name"])}

        for proc in process_status.keys():
            if proc.lower() in running_processes:
                process_status[proc] = True

        logger.info(f"Process Check: {process_status}")
        return ProcessStatus(processes=process_status)

    except Exception as e:
        logger.error(f"Failed to check processes: {e}")
        return ProcessStatus(processes={"error": False})
