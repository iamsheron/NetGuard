import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


class TelegramNotifier:

    # ==================================================
    # INITIALIZE
    # ==================================================

    def __init__(self):

        self.bot_token = os.getenv(
            "NETGUARD_TELEGRAM_TOKEN"
        )

    # ==================================================
    # TELEGRAM SERVER URL
    # ==================================================

    def get_telegram_server_url(self):

        tunnel_file = os.path.join(
            os.path.dirname(__file__),
            "telegram_tunnel.json"
        )

        if not os.path.exists(tunnel_file):

            print(
                "⚠ Telegram tunnel URL not available."
            )

            return None

        try:

            with open(
                tunnel_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            tunnel_url = data.get(
                "tunnel_url"
            )

            if tunnel_url:

                return tunnel_url.rstrip("/")

        except Exception as error:

            print(
                "⚠ Could not read Telegram tunnel:",
                error
            )

        print(
            "⚠ Telegram tunnel URL not available."
        )

        return None

    # ==================================================
    # INSTALLATION ID
    # ==================================================

    def get_installation_id(self):

        try:

            installation_file = os.path.join(
                os.path.dirname(__file__),
                "gui",
                "netguard_installation.json"
            )

            if not os.path.exists(
                installation_file
            ):

                print(
                    "⚠ NETGUARD installation file not found:"
                )

                print(
                    installation_file
                )

                return None

            with open(
                installation_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            installation_id = data.get(
                "installation_id"
            )

            return installation_id

        except Exception as error:

            print(
                "❌ Failed to read installation ID:",
                error
            )

            return None

    # ==================================================
    # GET CONNECTED TELEGRAM CHAT
    # ==================================================

    def get_connected_chat_id(self):

        installation_id = (
            self.get_installation_id()
        )

        if not installation_id:

            return None

        server_url = (
            self.get_telegram_server_url()
        )

        if not server_url:

            return None

        url = (
            f"{server_url}"
            f"/connection/status/"
            f"{installation_id}"
        )

        try:

            response = requests.get(
                url,
                timeout=10
            )

            if not response.ok:

                print(
                    "❌ Telegram connection status error:",
                    response.text
                )

                return None

            data = response.json()

            if not data.get("connected"):

                print(
                    "⚠ Telegram is not connected."
                )

                return None

            chat_id = data.get(
                "chat_id"
            )

            if not chat_id:

                print(
                    "⚠ Connected Telegram has no chat ID."
                )

                return None

            return str(chat_id)

        except requests.RequestException as error:

            print(
                "❌ Could not contact Telegram server:",
                error
            )

            return None

    # ==================================================
    # ENABLED
    # ==================================================

    def enabled(self):

        if not self.bot_token:

            return False

        return bool(
            self.get_connected_chat_id()
        )

    # ==================================================
    # SEND MESSAGE
    # ==================================================

    def send(self, message):

        if not self.bot_token:

            print(
                "⚠ Telegram bot token is not configured."
            )

            return False

        chat_id = (
            self.get_connected_chat_id()
        )

        if not chat_id:

            print(
                "⚠ No connected Telegram account found."
            )

            return False

        url = (
            "https://api.telegram.org/"
            f"bot{self.bot_token}/sendMessage"
        )

        try:

            response = requests.post(
                url,
                data={
                    "chat_id": chat_id,
                    "text": message
                },
                timeout=10
            )

            if response.ok:

                print(
                    f"📱 Telegram alert sent to {chat_id}."
                )

                return True

            print(
                "❌ Telegram error:",
                response.text
            )

            return False

        except requests.RequestException as error:

            print(
                "❌ Telegram notification failed:",
                error
            )

            return False

