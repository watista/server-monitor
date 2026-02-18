#!/usr/bin/python3

import time
import traceback
from typing import Optional
from services.logger import logger


class Alerts:
    """Singleton class to store notification alerts settings."""
    _instance: Optional["Alerts"] = None

    # Policy:
    BURST_INTERVAL_SECONDS = 5
    BURST_MAX_SENDS = 3
    STEADY_INTERVAL_SECONDS = 3600

    def __new__(cls) -> "Alerts":
        """Ensures only one instance of Alerts exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(Alerts, cls).__new__(cls)
            cls._instance._load_alerts()
        return cls._instance

    def _load_alerts(self) -> None:
        """Initialize default alert settings with mute state and active status."""
        self.alerts = {
            "ip": {"mute_until": 0, "active_alert": False, "burst_sent": 0, "last_sent": 0},
            "apt": {"mute_until": 0, "active_alert": False, "burst_sent": 0, "last_sent": 0},
            "disk": {"mute_until": 0, "active_alert": False, "burst_sent": 0, "last_sent": 0},
            "load": {"mute_until": 0, "active_alert": False, "burst_sent": 0, "last_sent": 0},
            "memory": {"mute_until": 0, "active_alert": False, "burst_sent": 0, "last_sent": 0},
            "users": {"mute_until": 0, "active_alert": False, "burst_sent": 0, "last_sent": 0},
            "processes": {"mute_until": 0, "active_alert": False, "burst_sent": 0, "last_sent": 0},
            "monitor": {"mute_until": 0, "active_alert": False, "burst_sent": 0, "last_sent": 0}
        }

    def mute_alert(self, alert_key: str, duration_hours: int) -> None:
        """Mute a specific alert for a given duration in hours."""
        try:
            self.alerts[alert_key]["mute_until"] = time.time() + (duration_hours * 3600)
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

    def reset_alert(self, alert_key: str) -> None:
        """Reset throttling counters when an alert is fixed."""
        try:
            self.alerts[alert_key]["active_alert"] = False
            self.alerts[alert_key]["burst_sent"] = 0
            self.alerts[alert_key]["last_sent"] = 0
        except Exception as e:
            logger.error(f"Error resetting alert {alert_key}, error: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")

    def mark_active(self, alert_key: str) -> None:
        """Mark alert as active; if this is a new activation, reset throttling."""
        try:
            if not self.alerts[alert_key]["active_alert"]:
                # Transition: inactive -> active
                self.alerts[alert_key]["active_alert"] = True
                self.alerts[alert_key]["burst_sent"] = 0
                self.alerts[alert_key]["last_sent"] = 0
        except Exception as e:
            logger.error(f"Error marking alert active {alert_key}, error: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")

    def should_send(self, alert_key: str) -> bool:
        try:
            if self.is_muted(alert_key):
                return False

            now = time.time()
            state = self.alerts[alert_key]

            # If it's not active, do not send (and don't mutate counters)
            if not state["active_alert"]:
                return False

            burst_sent = int(state.get("burst_sent", 0))
            last_sent = float(state.get("last_sent", 0))

            interval = self.BURST_INTERVAL_SECONDS if burst_sent < self.BURST_MAX_SENDS else self.STEADY_INTERVAL_SECONDS

            # First send after activation happens immediately (last_sent == 0)
            if last_sent == 0 or (now - last_sent) >= interval:
                state["last_sent"] = now
                if burst_sent < self.BURST_MAX_SENDS:
                    state["burst_sent"] = burst_sent + 1
                return True

            return False

        except Exception as e:
            logger.error(f"Error in should_send for {alert_key}, error: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return False


# Global instance of Alerts
alerts = Alerts()
