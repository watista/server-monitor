#!/usr/bin/python3

import time
from typing import Optional
from services.logger import logger


class Alerts:
    """Singleton class to store notification alerts settings."""
    _instance: Optional["Alerts"] = None

    def __new__(cls) -> "Alerts":
        """Ensures only one instance of Alerts exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(Alerts, cls).__new__(cls)
            cls._instance._load_alerts()
        return cls._instance

    def _load_alerts(self) -> None:
        """Initialize default alert settings with mute state and active status."""
        self.alerts = {
            "ip": {"mute_until": 0, "active_alert": False},
            "apt": {"mute_until": 0, "active_alert": False},
            "disk": {"mute_until": 0, "active_alert": False},
            "load": {"mute_until": 0, "active_alert": False},
            "memory": {"mute_until": 0, "active_alert": False},
            "users": {"mute_until": 0, "active_alert": False},
            "processes": {"mute_until": 0, "active_alert": False}
        }

    def mute_alert(self, alert_key: str, duration_hours: int) -> None:
        """Mute a specific alert for a given duration in hours."""
        try:
            self.alerts[alert_key]["mute_until"] = time.time() + \
                (duration_hours * 3600)
            return
        except Exception as e:
            logger.error(f"Error handling muting alert {alert_key}, error: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return None

    def is_muted(self, alert_key: str) -> bool:
        """Check if an alert is muted."""
        try:
            return time.time() < self.alerts[alert_key]["mute_until"]
        except Exception as e:
            logger.error(f"Error handling check mute alert {alert_key}, error: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return None

    def unmute_alert(self, alert_key: str) -> bool:
        """Unmute a specific alert."""
        try:
            self.alerts[alert_key]["mute_until"] = 0
            return
        except Exception as e:
            logger.error(f"Error handling unmuting alert {alert_key}, error: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return None


# Global instance of Alerts
alerts = Alerts()
