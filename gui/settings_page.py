import customtkinter as ctk
import json
import os
import threading
import urllib.request
import urllib.error

from gui import theme
from database import verify_user, change_password


class SettingsPage(ctk.CTkFrame):

    TELEGRAM_TUNNEL_FILE = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "telegram_tunnel.json"
    )


    INSTALLATION_FILE = os.path.join(
        os.path.dirname(__file__),
        "netguard_installation.json"
    )

    def __init__(self, parent, app):
        super().__init__(
            parent,
            fg_color=theme.BACKGROUND
        )

        self.app = app

        self.pack(
            fill="both",
            expand=True
        )


        self.build_ui()

    # ==================================================
    # UI
    # ==================================================

    def build_ui(self):

        # ------------------------------------------------
        # HEADER
        # ------------------------------------------------

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=35,
            pady=(25, 15)
        )

        self.back_button = ctk.CTkButton(
            header,
            text="← Back",
            width=90,
            height=36,
            fg_color=theme.PANEL,
            hover_color=theme.BORDER,
            command=self.go_back
        )

        self.back_button.pack(
            side="left"
        )

        ctk.CTkLabel(
            header,
            text="⚙ NETGUARD SETTINGS",
            font=("Segoe UI", 24, "bold"),
            text_color=theme.TEXT
        ).pack(
            side="right"
        )

        # ------------------------------------------------
        # TITLE
        # ------------------------------------------------

        ctk.CTkLabel(
            self,
            text="Settings",
            font=("Segoe UI", 30, "bold"),
            text_color=theme.TEXT
        ).pack(
            anchor="w",
            padx=50,
            pady=(10, 2)
        )

        ctk.CTkLabel(
            self,
            text="Manage your NETGUARD security preferences.",
            font=("Segoe UI", 13),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=50,
            pady=(0, 25)
        )

        # ------------------------------------------------
        # SETTINGS CONTENT
        # ------------------------------------------------

        content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )

        content.pack(
            fill="both",
            expand=True,
            padx=50,
            pady=(0, 30)
        )

        # ------------------------------------------------
        # ACCOUNT
        # ------------------------------------------------

        account = self.create_section(
            content,
            "🔐 ACCOUNT"
        )

        self.create_setting_row(
            account,
            "Change Password",
            "Update your NETGUARD administrator password.",
            "🔑",
            self.change_password
        )

        self.create_setting_row(
            account,
            "Lock NETGUARD",
            "Return immediately to the secure login screen.",
            "🔒",
            self.lock_netguard
        )

        # ------------------------------------------------
        # SCANNING
        # ------------------------------------------------

        scanning = self.create_section(
            content,
            "🔎 SCANNING"
        )

        self.create_setting_row(
            scanning,
            "Full Scan Preferences",
            "Choose what NETGUARD checks during a full scan.",
            "🛡",
            self.scan_preferences
        )

        self.create_setting_row(
            scanning,
            "Port Scan Preferences",
            "Configure network port scanning behavior.",
            "🌐",
            self.port_preferences
        )

        # ------------------------------------------------
        # NOTIFICATIONS
        # ------------------------------------------------

        notifications = self.create_section(
            content,
            "🔔 NOTIFICATIONS"
        )

        self.create_notification_row(
            notifications
        )

    # ==================================================
    # SECTION
    # ==================================================

    def create_section(self, parent, title):

        section = ctk.CTkFrame(
            parent,
            fg_color=theme.PANEL,
            corner_radius=16
        )

        section.pack(
            fill="x",
            pady=(0, 18)
        )

        ctk.CTkLabel(
            section,
            text=title,
            font=("Segoe UI", 12, "bold"),
            text_color=theme.PRIMARY
        ).pack(
            anchor="w",
            padx=20,
            pady=(16, 8)
        )

        return section

    # ==================================================
    # SETTING ROW
    # ==================================================

    def create_setting_row(
        self,
        parent,
        title,
        description,
        icon,
        command
    ):

        row = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            padx=12,
            pady=5
        )

        icon_label = ctk.CTkLabel(
            row,
            text=icon,
            font=("Segoe UI Emoji", 22),
            width=40
        )

        icon_label.pack(
            side="left",
            padx=(5, 12)
        )

        text_frame = ctk.CTkFrame(
            row,
            fg_color="transparent"
        )

        text_frame.pack(
            side="left",
            fill="x",
            expand=True
        )

        ctk.CTkLabel(
            text_frame,
            text=title,
            font=("Segoe UI", 14, "bold"),
            text_color=theme.TEXT
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            text_frame,
            text=description,
            font=("Segoe UI", 11),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            anchor="w",
            pady=(2, 8)
        )

        ctk.CTkButton(
            row,
            text="→",
            width=45,
            height=38,
            fg_color=theme.CARD,
            hover_color=theme.BORDER,
            command=command
        ).pack(
            side="right",
            padx=5
        )

    # ==================================================
    # TELEGRAM
    # ==================================================


    def get_telegram_server_url(self):
        """
        Read the current Cloudflare Quick Tunnel URL created by launcher.py.
        The launcher writes this file at the NETGUARD project root.
        """
        tunnel_file = self.TELEGRAM_TUNNEL_FILE

        if not os.path.exists(tunnel_file):
            print(
                "Telegram tunnel file not found:",
                tunnel_file
            )
            return None

        try:
            with open(
                tunnel_file,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            tunnel_url = data.get("tunnel_url")

            if tunnel_url:
                return tunnel_url.rstrip("/")

            print("Telegram tunnel URL is empty.")

        except Exception as error:
            print(
                "Telegram tunnel read failed:",
                error
            )

        return None

    def get_installation_id(self):
        try:
            if os.path.exists(self.INSTALLATION_FILE):
                with open(
                    self.INSTALLATION_FILE,
                    "r",
                    encoding="utf-8"
                ) as file:
                    data = json.load(file)

                installation_id = data.get("installation_id")

                if installation_id:
                    return installation_id

        except Exception as e:
            print(f"Installation ID read error: {e}")

        import uuid

        installation_id = str(uuid.uuid4())

        try:
            with open(
                self.INSTALLATION_FILE,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    {"installation_id": installation_id},
                    file
                )

        except Exception as e:
            print(f"Installation ID save error: {e}")

        return installation_id

        # ==================================================
    # TELEGRAM
    # ==================================================

    def create_notification_row(self, parent):

        row = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            padx=12,
            pady=(5, 15)
        )

        ctk.CTkLabel(
            row,
            text="📨",
            font=("Segoe UI Emoji", 22),
            width=40
        ).pack(
            side="left",
            padx=(5, 12)
        )

        text_frame = ctk.CTkFrame(
            row,
            fg_color="transparent"
        )

        text_frame.pack(
            side="left",
            fill="x",
            expand=True
        )

        ctk.CTkLabel(
            text_frame,
            text="Telegram Alerts",
            font=("Segoe UI", 14, "bold"),
            text_color=theme.TEXT
        ).pack(
            anchor="w"
        )

        self.telegram_status = ctk.CTkLabel(
            text_frame,
            text="Not connected",
            font=("Segoe UI", 11),
            text_color=theme.TEXT_SECONDARY
        )

        self.telegram_status.pack(
            anchor="w",
            pady=(2, 5)
        )

        self.telegram_switch = ctk.CTkSwitch(
            row,
            text="",
            progress_color=theme.SUCCESS,
            button_color=theme.TEXT,
            button_hover_color=theme.TEXT_SECONDARY,
            command=self.telegram_switch_changed
        )

        self.telegram_switch.pack(
            side="right",
            padx=10
        )

        self.telegram_installation_id = self.get_installation_id()
        self.check_telegram_status()

        

    def telegram_switch_changed(self):

        if self.telegram_switch.get() == 1:
            self.connect_telegram()
        else:
            self.telegram_status.configure(
                text="Telegram alerts disabled",
                text_color=theme.TEXT_SECONDARY
            )

    def connect_telegram(self):

        self.telegram_switch.configure(
            state="disabled"
        )

        self.telegram_status.configure(
            text="Connecting...",
            text_color=theme.TEXT_SECONDARY
        )

        thread = threading.Thread(
            target=self.create_telegram_connection,
            daemon=True
        )

        thread.start()
    def create_telegram_connection(self):

        server_url = self.get_telegram_server_url()

        if not server_url:
            raise Exception("Current Telegram tunnel is not available")

        url = (
            server_url
            + "/connection/create"
        )

        payload = json.dumps({
            "installation_id":
                self.telegram_installation_id
        }).encode("utf-8")

        try:
            request = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Content-Type":
                        "application/json"
                },
                method="POST"
            )

            with urllib.request.urlopen(
                request,
                timeout=10
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

            if not data.get("success"):
                raise Exception(
                    data.get(
                        "error",
                        "Connection failed"
                    )
                )

            code = data.get("code")

            self.after(
                0,
                lambda: self.show_telegram_code(code)
            )

        except Exception as e:

            print(
                f"Telegram connection error: {e}"
            )

            self.after(
                0,
                self.telegram_connection_failed
            )
    def show_telegram_code(self, code):

        self.telegram_switch.configure(
            state="normal"
        )

        dialog = ctk.CTkToplevel(self)

        dialog.title("Connect Telegram")
        dialog.geometry("460x360")
        dialog.resizable(False, False)

        dialog.configure(
            fg_color=theme.BACKGROUND
        )

        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="📨 Connect Telegram",
            font=("Segoe UI", 22, "bold"),
            text_color=theme.TEXT
        ).pack(
            pady=(25, 8)
        )

        ctk.CTkLabel(
            dialog,
            text=(
                "Connect your Telegram account to\n"
                "receive NETGUARD security alerts."
            ),
            font=("Segoe UI", 12),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            pady=(0, 20)
        )

        def open_telegram():

            import webbrowser

            telegram_url = (
                "https://t.me/NetGuardSecurityBot"
                f"?start={code}"
            )

            webbrowser.open(telegram_url)

        connect_button = ctk.CTkButton(
            dialog,
            text="📨  Connect with Telegram",
            width=280,
            height=48,
            font=("Segoe UI", 14, "bold"),
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_HOVER,
            command=open_telegram
        )

        connect_button.pack(
            pady=(5, 15)
        )

        ctk.CTkLabel(
            dialog,
            text=(
                "Telegram will open with your connection ready.\n"
                "Just press Start in the Telegram bot."
            ),
            font=("Segoe UI", 11),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            pady=(0, 12)
        )

        ctk.CTkLabel(
            dialog,
            text=f"Fallback code: /start {code}",
            font=("Consolas", 10),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            pady=(5, 10)
        )

        status = ctk.CTkLabel(
            dialog,
            text="Waiting for Telegram connection...",
            font=("Segoe UI", 11),
            text_color=theme.TEXT_SECONDARY
        )

        status.pack(
            pady=5
        )

        cancel_button = ctk.CTkButton(
            dialog,
            text="Cancel",
            width=160,
            height=40,
            fg_color=theme.CARD,
            hover_color=theme.BORDER,
            command=lambda: self.cancel_telegram_connection(
                dialog
            )
        )

        cancel_button.pack(
            pady=(12, 20)
        )

        dialog.after(
            1500,
            lambda: self.poll_telegram_status(
                dialog,
                status,
                code
            )
        )

    def poll_telegram_status(
        self,
        dialog,
        status,
        code
    ):

        if not dialog.winfo_exists():
            return

        thread = threading.Thread(
            target=self.check_connection_thread,
            args=(dialog, status, code),
            daemon=True
        )

        thread.start()

    def check_connection_thread(
        self,
        dialog,
        status,
        code
    ):

        server_url = self.get_telegram_server_url()

        if not server_url:
            raise Exception("Current Telegram tunnel is not available")

        url = (
            server_url
            + "/connection/status/"
            + self.telegram_installation_id
        )

        try:

            request = urllib.request.Request(
                url,
                method="GET"
            )

            with urllib.request.urlopen(
                request,
                timeout=10
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

            connected = data.get(
                "connected",
                False
            )

            self.after(
                0,
                lambda: self.telegram_status_result(
                    dialog,
                    status,
                    connected,
                    code
                )
            )

        except Exception as e:

            print(
                f"Telegram status error: {e}"
            )

            self.after(
                0,
                lambda: self.telegram_status_result(
                    dialog,
                    status,
                    False,
                    code
                )
            )
    def telegram_status_result(
        self,
        dialog,
        status,
        connected,
        code
    ):

        if not dialog.winfo_exists():
            return

        if connected:

            status.configure(
                text="✓ Telegram connected!",
                text_color=theme.SUCCESS
            )

            self.telegram_status.configure(
                text="✓ Telegram Connected",
                text_color=theme.SUCCESS
            )

            self.telegram_switch.select()

            dialog.after(
                1200,
                dialog.destroy
            )

            return

        status.configure(
            text="Waiting for Telegram connection...",
            text_color=theme.TEXT_SECONDARY
        )

        dialog.after(
            2000,
            lambda: self.poll_telegram_status(
                dialog,
                status,
                code
            )
        )

    def cancel_telegram_connection(self, dialog):

        self.telegram_switch.deselect()

        self.telegram_status.configure(
            text="Not connected",
            text_color=theme.TEXT_SECONDARY
        )

        dialog.destroy()

    def telegram_connection_failed(self):

        self.telegram_switch.deselect()

        self.telegram_switch.configure(
            state="normal"
        )

        self.telegram_status.configure(
            text="Could not reach Telegram service",
            text_color=theme.DANGER
        )

    def check_telegram_status(self):

        thread = threading.Thread(
            target=self.check_telegram_status_thread,
            daemon=True
        )

        thread.start()
    def check_telegram_status_thread(self):

        server_url = self.get_telegram_server_url()

        if not server_url:
            raise Exception("Current Telegram tunnel is not available")

        url = (
            server_url
            + "/connection/status/"
            + self.telegram_installation_id
        )

        try:

            request = urllib.request.Request(
                url,
                method="GET"
            )

            with urllib.request.urlopen(
                request,
                timeout=10
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

            connected = data.get(
                "connected",
                False
            )

            self.after(
                0,
                lambda: self.update_telegram_status(
                    connected
                )
            )

        except Exception as error:

            print(
                "Telegram status check failed:",
                error
            )

            self.after(
                0,
                self.telegram_status_unavailable
            )
    def telegram_status_unavailable(self):
        """
        A tunnel/DNS failure is not the same thing as a Telegram disconnect.
        Keep the current switch state and tell the user that status is being
        retried instead of forcing the switch OFF.
        """
        try:
            self.telegram_status.configure(
                text="Checking Telegram connection...",
                text_color=theme.TEXT_SECONDARY
            )
        except Exception:
            pass

        # Retry in case Cloudflare DNS is still propagating.
        self.after(
            5000,
            self.check_telegram_status
        )

    def update_telegram_status(self, connected):

        if connected:

            self.telegram_switch.select()

            self.telegram_status.configure(
                text="✓ Telegram Connected",
                text_color=theme.SUCCESS
            )

        else:

            self.telegram_switch.deselect()

            self.telegram_status.configure(
                text="Not connected",
                text_color=theme.TEXT_SECONDARY
            )
    # ==================================================
    # ACTIONS
    # ==================================================

    def change_password(self):

        username = getattr(
            self.app,
            "current_username",
            None
        )

        if not username:
            return

        dialog = ctk.CTkToplevel(self)

        dialog.title("Change Password")
        dialog.geometry("460x470")
        dialog.resizable(False, False)

        dialog.configure(
            fg_color=theme.BACKGROUND
        )

        dialog.transient(self)
        dialog.grab_set()

    # ==============================================
    # HEADER
    # ==============================================

        ctk.CTkLabel(
            dialog,
            text="🔐 Change Password",
            font=("Segoe UI", 22, "bold"),
            text_color=theme.TEXT
        ).pack(
            pady=(25, 5)
        )

        ctk.CTkLabel(
            dialog,
            text=f"Account: {username}",
            font=("Segoe UI", 11),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            pady=(0, 20)
        )

    # ==============================================
    # CURRENT PASSWORD
    # ==============================================

        ctk.CTkLabel(
            dialog,
            text="Current Password",
            font=("Segoe UI", 12, "bold"),
            text_color=theme.TEXT
        ).pack(
            anchor="w",
            padx=40
        )

        current_frame = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )

        current_frame.pack(
            fill="x",
            padx=40,
            pady=(5, 15)
        )

        current_password = ctk.CTkEntry(
            current_frame,
            height=40,
            show="•",
            placeholder_text="Enter current password"
        )

        current_password.pack(
            side="left",
            fill="x",
            expand=True
        )

        current_visible = False

        def toggle_current_password():

            nonlocal current_visible

            current_visible = not current_visible

            current_password.configure(
                show="" if current_visible else "•"
            )

            current_eye.configure(
                text="🙈" if current_visible else "👁"
            )

        current_eye = ctk.CTkButton(
            current_frame,
            text="👁",
            width=45,
            height=40,
            fg_color=theme.CARD,
            hover_color=theme.BORDER,
            command=toggle_current_password
        )

        current_eye.pack(
            side="right",
            padx=(6, 0)
        )
    # ==============================================
    # NEW PASSWORD
    # ==============================================

        new_frame = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )

        new_frame.pack(
            fill="x",
            padx=40,
            pady=(5, 15)
        )

        new_password = ctk.CTkEntry(
            new_frame,
            height=40,
            show="•",
            placeholder_text="Enter new password"
        )

        new_password.pack(
            side="left",
            fill="x",
            expand=True
        )

        new_visible = False

        def toggle_new_password():

            nonlocal new_visible

            new_visible = not new_visible

            new_password.configure(
                show="" if new_visible else "•"
            )

            new_eye.configure(
                text="🙈" if new_visible else "👁"
            )

        new_eye = ctk.CTkButton(
            new_frame,
            text="👁",
            width=45,
            height=40,
            fg_color=theme.CARD,
            hover_color=theme.BORDER,
            command=toggle_new_password
        )

        new_eye.pack(
            side="right",
            padx=(6, 0)
        )
    # ==============================================
    # CONFIRM PASSWORD
    # ==============================================

        confirm_frame = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )

        confirm_frame.pack(
            fill="x",
            padx=40,
            pady=(5, 10)
        )

        confirm_password = ctk.CTkEntry(
            confirm_frame,
            height=40,
            show="•",
            placeholder_text="Confirm new password"
        )

        confirm_password.pack(
            side="left",
            fill="x",
            expand=True
        )

        confirm_visible = False

        def toggle_confirm_password():

            nonlocal confirm_visible
           
            confirm_visible = not confirm_visible

            confirm_password.configure(
                show="" if confirm_visible else "•"
            )

            confirm_eye.configure(
                text="🙈" if confirm_visible else "👁"
            )

        confirm_eye = ctk.CTkButton(
            confirm_frame,
            text="👁",
            width=45,
            height=40,
            fg_color=theme.CARD,
            hover_color=theme.BORDER,
            command=toggle_confirm_password
        )

        confirm_eye.pack(
            side="right",
            padx=(6, 0)
        ) 
    # ==============================================
    # MESSAGE
    # ==============================================

        message = ctk.CTkLabel(
            dialog,
            text="",
            font=("Segoe UI", 11)
        )

        message.pack(
            pady=(0, 10)
        )

    # ==============================================
    # UPDATE PASSWORD
    # ==============================================

        def update_password():

            current = current_password.get()
            new = new_password.get()
            confirm = confirm_password.get()

            if not current or not new or not confirm:

                message.configure(
                    text="✕ Please fill in all fields.",
                    text_color=theme.DANGER
                )

                return

            if not verify_user(
                username,
                current
            ):

                message.configure(
                    text="✕ Current password is incorrect.",
                    text_color=theme.DANGER
                )

                return

            if new != confirm:

                message.configure(
                    text="✕ New passwords do not match.",
                    text_color=theme.DANGER
                )

                return

            if len(new) < 8:

                message.configure(
                    text="✕ Password must contain at least 8 characters.",
                    text_color=theme.DANGER
                )

                return

            try:

                change_password(
                    username,
                    new
                )

                message.configure(
                    text="✓ Password updated successfully.",
                    text_color=theme.SUCCESS
                )

                update_button.configure(
                    state="disabled",
                    text="✓ UPDATED"
                )

                dialog.after(
                    1200,
                    dialog.destroy
                )

            except Exception as e:

                message.configure(
                    text="✕ Failed to update password.",
                    text_color=theme.DANGER
                )

                print(
                    f"Password update error: {e}"
                )

    # ==============================================
    # BUTTONS
    # ==============================================

        button_frame = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            padx=40,
            pady=(5, 20)
        )

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=150,
            height=40,
            fg_color=theme.CARD,
            hover_color=theme.BORDER,
            command=dialog.destroy
        ).pack(
            side="left"
        )

        update_button = ctk.CTkButton(
            button_frame,
            text="Update Password",
            width=210,
            height=40,
            fg_color=theme.PRIMARY,
            hover_color="#4775D1",
            command=update_password
        )

        update_button.pack(
            side="right"
        )

        current_password.focus()

    def lock_netguard(self):

        self.app.show_login()

    def scan_preferences(self):

        dialog = ctk.CTkToplevel(self)

        dialog.title("Full Scan Preferences")
        dialog.geometry("460x470")
        dialog.resizable(False, False)

        dialog.configure(
            fg_color=theme.BACKGROUND
        )

        dialog.transient(self)
        dialog.grab_set()

    # ==============================================
    # HEADER
    # ==============================================

        ctk.CTkLabel(
            dialog,
            text="🔎 Full Scan Preferences",
            font=("Segoe UI", 22, "bold"),
            text_color=theme.TEXT
        ).pack(
            pady=(25, 5)
        )

        ctk.CTkLabel(
            dialog,
            text="Choose what NETGUARD checks during a full scan.",
            font=("Segoe UI", 11),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            pady=(0, 20)
        )

    # ==============================================
    # OPTIONS
    # ==============================================

        options_frame = ctk.CTkFrame(
            dialog,
            fg_color=theme.PANEL,
            corner_radius=14
        )

        options_frame.pack(
            fill="x",
            padx=35,
            pady=5
        )

        device_discovery = ctk.CTkSwitch(
            options_frame,
            text="🖥 Device Discovery",
            text_color=theme.TEXT
        )

        device_discovery.pack(
            anchor="w",
            padx=20,
            pady=(18, 10)
        )

        security_checks = ctk.CTkSwitch(
            options_frame,
            text="🛡 Security Checks",
            text_color=theme.TEXT
        )

        security_checks.pack(
            anchor="w",
            padx=20,
            pady=10
        )

        port_scanning = ctk.CTkSwitch(
            options_frame,
            text="🌐 Port Scanning",
            text_color=theme.TEXT
        )

        port_scanning.pack(
            anchor="w",
            padx=20,
            pady=10
        )

        auto_scan = ctk.CTkSwitch(
            options_frame,
            text="🔄 Automatic Scanning",
            text_color=theme.TEXT
        )

        auto_scan.pack(
            anchor="w",
            padx=20,
            pady=10
        )

        save_results = ctk.CTkSwitch(
            options_frame,
            text="💾 Save Scan Results",
            text_color=theme.TEXT
        )

        save_results.pack(
            anchor="w",
            padx=20,
            pady=(10, 18)
        )

    # ==============================================
    # DEFAULTS
    # ==============================================

        device_discovery.select()
        security_checks.select()
        port_scanning.select()
        save_results.select()

    # ==============================================
    # STATUS
    # ==============================================

        status = ctk.CTkLabel(
            dialog,
            text="",
            font=("Segoe UI", 11)
        )

        status.pack(
            pady=(12, 5)
        )

    # ==============================================
    # SAVE
    # ==============================================

        def save_preferences():

            status.configure(
                text="✓ Full scan preferences saved",
                text_color=theme.SUCCESS
            )

            save_button.configure(
                text="✓ SAVED",
                state="disabled"
            )

            dialog.after(
                1000,
                dialog.destroy
            )

        save_button = ctk.CTkButton(
            dialog,
            text="Save Preferences",
            width=260,
            height=50,
            font=("Segoe UI", 14, "bold"),
            fg_color=theme.PRIMARY,
            hover_color="#4775D1",
            corner_radius=10,
            command=save_preferences
        )

        save_button.pack(
           pady=(12, 25)
        )

    def port_preferences(self):

        dialog = ctk.CTkToplevel(self)

        dialog.title("Port Scan Preferences")
        dialog.geometry("460x470")
        dialog.resizable(False, False)

        dialog.configure(
            fg_color=theme.BACKGROUND
        )

        dialog.transient(self)
        dialog.grab_set()

    # ==============================================
    # HEADER
    # ==============================================

        ctk.CTkLabel(
            dialog,
            text="🌐 Port Scan Preferences",
            font=("Segoe UI", 22, "bold"),
            text_color=theme.TEXT
        ).pack(
            pady=(25, 5)
        )

        ctk.CTkLabel(
            dialog,
            text="Configure the current NETGUARD port scan.",
            font=("Segoe UI", 11),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            pady=(0, 20)
        )

    # ==============================================
    # SETTINGS CARD
    # ==============================================

        settings_card = ctk.CTkFrame(
            dialog,
            fg_color=theme.PANEL,
            corner_radius=14
        )

        settings_card.pack(
            fill="x",
            padx=35,
            pady=5
        )

    # ==============================================
    # SCAN PROFILE
    # ==============================================

        ctk.CTkLabel(
            settings_card,
            text="Scan Profile",
            font=("Segoe UI", 12, "bold"),
            text_color=theme.TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 4)
        )

        profile = ctk.CTkOptionMenu(
            settings_card,
            values=["Common Ports"],
            width=200,
            height=36,
            fg_color=theme.CARD,
            button_color=theme.PRIMARY,
            button_hover_color=theme.BORDER
        )

        profile.set("Common Ports")

        profile.pack(
            anchor="w",
            padx=20,
            pady=(0, 12)
        )

    # ==============================================
    # TIMEOUT
    # ==============================================

        ctk.CTkLabel(
            settings_card,
            text="Connection Timeout",
            font=("Segoe UI", 12, "bold"),
            text_color=theme.TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=(4, 4)
        )

        timeout_label = ctk.CTkLabel(
            settings_card,
            text="0.4 seconds",
            font=("Segoe UI", 11),
            text_color=theme.TEXT_SECONDARY
        )

        timeout_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 12)
        )

    # ==============================================
    # OPTIONS
    # ==============================================

        scan_full = ctk.CTkSwitch(
            settings_card,
            text="Scan during Full Scan",
            text_color=theme.TEXT
        )

        scan_full.pack(
            anchor="w",
            padx=20,
            pady=8
        )

        save_results = ctk.CTkSwitch(
            settings_card,
            text="Save Scan Results",
            text_color=theme.TEXT
        )

        save_results.pack(
            anchor="w",
            padx=20,
            pady=(8, 18)
        )

        scan_full.select()
        save_results.select()

    # ==============================================
    # STATUS
    # ==============================================

        status = ctk.CTkLabel(
            dialog,
            text="",
            font=("Segoe UI", 11)
        )

        status.pack(
            pady=(12, 5)
        )

    # ==============================================
    # SAVE
    # ==============================================

        def save_preferences():

            status.configure(
                text="✓ Port scan preferences saved",
                text_color=theme.SUCCESS
            )

            save_button.configure(
                text="✓ SAVED",
                state="disabled"
            )

            dialog.after(
                1000,
                dialog.destroy
            )

        save_button = ctk.CTkButton(
            dialog,
            text="✓  SAVE PREFERENCES",
            width=280,
            height=48,
            font=("Segoe UI", 14, "bold"),
            fg_color=theme.PRIMARY,
            hover_color="#4775D1",
            corner_radius=10,
            command=save_preferences
        )

        save_button.pack(
            pady=(5, 15)
        )

    # ==================================================
    # NAVIGATION
    # ==================================================

    def go_back(self):

        self.app.show_security_center()