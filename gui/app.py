import customtkinter as ctk
from database import create_database

from gui import theme
from gui.login import LoginPage
from gui.dashboard import DashboardPage
from gui.security_center import SecurityCenterPage
from gui.settings_page import SettingsPage



class NetGuardApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ---------------- Window ----------------

        self.title("NetGuard Enterprise")
        self.geometry("1400x850")
        self.minsize(1200,750)

        self.configure(fg_color=theme.BACKGROUND)

        self.create_layout()

        create_database()

        self.show_login()

    # ----------------------------------------
    # Layout
    # ----------------------------------------

    def create_layout(self):

        # Header

        self.header = ctk.CTkFrame(
            self,
            height=70,
            fg_color=theme.PANEL,
            corner_radius=0
        )

        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.logo = ctk.CTkLabel(
            self.header,
            text="🛡 NetGuard",
            font=theme.HEADING_FONT
        )

        self.logo.pack(side="left", padx=25)

        self.version = ctk.CTkLabel(
            self.header,
            text="Enterprise v1.0",
            font=theme.SMALL_FONT
        )

        self.version.pack(side="right", padx=25)

        # Main Content

        self.content = ctk.CTkFrame(
            self,
            fg_color=theme.BACKGROUND,
            corner_radius=0
        )

        self.content.pack(fill="both", expand=True)

        # Status Bar

        self.status = ctk.CTkFrame(
            self,
            height=35,
            fg_color=theme.PANEL,
            corner_radius=0
        )

        self.status.pack(fill="x")
        self.status.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.status,
            text="Ready",
            font=theme.SMALL_FONT
        )

        self.status_label.pack(side="left", padx=15)

    # ----------------------------------------
    # Page System
    # ----------------------------------------

    def clear_page(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def show_login(self):

        self.clear_page()

        LoginPage(self.content, self)

    def show_dashboard(self):

        self.clear_page()

        DashboardPage(self.content, self)

    def show_security_center(self):

        for widget in self.content.winfo_children():
            widget.destroy()

        SecurityCenterPage(self.content, self)

    def show_settings(self):

        self.clear_page()

        SettingsPage(
            self.content,
            self
        )