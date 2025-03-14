#!/usr/bin/python3

import time
from typing import Optional


class Alerts:
    """Singleton class to store notification alerts settings."""
    _instance: Optional["Alerts"] = None

    def __new__(cls) -> "Alerts":
        if cls._instance is None:
            cls._instance = super(Alerts, cls).__new__(cls)
            cls._instance._load_alerts()
        return cls._instance

    def _load_alerts(self) -> None:
        """Set default empty dict for each alert type"""
        self.alerts = {
            "ip": {"muted": False, "mute_until": 0},
            "apt": {"muted": False, "mute_until": 0},
            "apt_security": {"muted": False, "mute_until": 0},
            "disk": {"muted": False, "mute_until": 0},
            "load": {"muted": True, "mute_until": 0},
            "memory": {"muted": False, "mute_until": 0},
            "swap": {"muted": False, "mute_until": 0},
            "users": {"muted": False, "mute_until": 0},
            "process1": {"muted": False, "mute_until": 0},
            "process2": {"muted": False, "mute_until": 0}
        }

    def mute_alert(self, alert_key: str, duration_hours: int) -> None:
        """Mute a specific alert for a given duration in hours."""
        try:
            self.alerts[alert_key]["muted"] = True
            self.alerts[alert_key]["mute_until"] = time.time() + (duration_hours * 3600)
            return
        except Exception as e:
            logger.error(f"Error handling muting alert {alert_key}, error: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return None

    def is_muted(self, alert_key: str) -> bool:
        """Check if an alert is muted."""
        try:
            return self.alerts[alert_key]["muted"] and time.time() < self.alerts[alert_key]["mute_until"]
        except Exception as e:
            logger.error(f"Error handling check mute alert {alert_key}, error: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return None

    def unmute_alert(self, alert_key: str) -> bool:
        """Unmute a specific alert."""
        try:
            self.alerts[alert_key]["muted"] = False
            self.alerts[alert_key]["mute_until"] = 0
            return
        except Exception as e:
            logger.error(f"Error handling unmuting alert {alert_key}, error: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return None


# Global instance of Alerts
alerts = Alerts()
