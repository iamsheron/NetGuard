from datetime import datetime
import uuid
from core import shared_state
from telegram_notifier import TelegramNotifier



class AlertManager:

    def __init__(self):
        self.alerts =  shared_state.alerts
        self.telegram = TelegramNotifier()

    def raise_alert(
        self,
        level,
        title,
        message,
        device=None
    ):

        alert = {
            "id": str(uuid.uuid4())[:8],
            "level": level,
            "title": title,
            "message": message,
            "device": device,
            "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }

        self.alerts.insert(0, alert)
        telegram_message = self.format_telegram_alert(alert)

        self.telegram.send(telegram_message)

        return alert


    def format_telegram_alert(self, alert):

        level = alert["level"]
        title = alert["title"]
        message = alert["message"]
        time = alert["time"]
        device = alert.get("device")

    # ==========================================
    # ARP SPOOFING ALERT
    # ==========================================

        if alert.get("title") == "🚨 ARP Spoofing Detected":

            ip = None
            expected_mac = None
            observed_mac = None

            if device:

                ip = device.get("ip")
                expected_mac = device.get("expected_mac")
                observed_mac = device.get("observed_mac")

                # If the detector stored the information
                # inside the alert message instead, use it
                # directly from the message.

            text = (
                "🛡 NETGUARD SECURITY ALERT\n\n"
                "🚨 ARP SPOOFING DETECTED\n\n"
                f"Severity: {level}\n"
                f"Time: {time}\n\n"
            )

            if ip:
                text += (
                "Target IP:\n"
                f"{ip}\n\n"
                )

            if expected_mac:
                text += (
                "Expected MAC:\n"
                f"{expected_mac}\n\n"
                )

            if observed_mac:
                text += (
                "Observed MAC:\n"
                f"{observed_mac}\n\n"
                )

            if message:
                text += (
                f"{message}\n\n"
                )

            text += (
                "⚠ Possible man-in-the-middle attack."
            )

            return text

    # ==========================================
    # NORMAL / ROGUE DEVICE ALERT
    # ==========================================

        text = (
            "🛡 NETGUARD SECURITY ALERT\n\n"
            f"{title}\n\n"
            f"Severity: {level}\n"
            f"Time: {time}\n\n"
            f"{message}"
            )

        if device:

            text += "\n\n"

            if device.get("device_name"):
                text += (
                    f"Device: "
                    f"{device['device_name']}\n"
                )

            if device.get("mac"):
                text += (
                    f"MAC: "
                    f"{device['mac']}\n"
                )

            if device.get("vendor"):
                text += (
                    f"Vendor: "
                    f"{device['vendor']}\n"
                )

        return text

    def get_alerts(self):
        return self.alerts

    def clear(self):
        self.alerts.clear()