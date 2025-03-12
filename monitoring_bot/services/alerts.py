#!/usr/bin/python3

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
            "ip": {"muted": False, "mute_until": 0, "last_alert": 0},
            "apt": {"muted": False, "mute_until": 0, "last_alert": 0},
            "apt_security": {"muted": False, "mute_until": 0, "last_alert": 0},
            "disk": {"muted": False, "mute_until": 0, "last_alert": 0},
            "load_1": {"muted": False, "mute_until": 0, "last_alert": 0},
            "load_5": {"muted": False, "mute_until": 0, "last_alert": 0},
            "load_15": {"muted": False, "mute_until": 0, "last_alert": 0},
            "ram": {"muted": False, "mute_until": 0, "last_alert": 0},
            "swap": {"muted": False, "mute_until": 0, "last_alert": 0},
            "users": {"muted": False, "mute_until": 0, "last_alert": 0}
        }

    def mute_alert(self, alert_key: str, duration_hours: int) -> None:
        """Mute a specific alert for a given duration in hours."""
        self.alerts[alert_key]["muted"] = True
        self.alerts[alert_key]["mute_until"] = time.time() + (duration_hours * 3600)

    def is_muted(self, alert_key: str) -> bool:
        """Check if an alert is muted."""
        return self.alerts[alert_key]["muted"] and time.time() < self.alerts[alert_key]["mute_until"]


# Global instance of Alerts
alerts = Alerts()
