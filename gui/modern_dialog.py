import customtkinter as ctk 
from gui import theme

class ModernDialog(ctk.CTkToplevel):

    def __init__(self, parent, icon, title, message, details=None):

        super().__init__(parent)

        self.geometry("620x460")
        self.title("NetGuard")

        self.configure(fg_color=theme.BACKGROUND)

        self.resizable(False, False)

        self.transient(parent)

        self.grab_set()

        self.details = details

        self.build_ui(icon, title, message)


    def build_ui(self, icon, title, message):

        container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )
        # ======================
        # Header
        # ======================

        header = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        header.pack(fill="x", pady=(0,20))

        ctk.CTkLabel(
            header,
            text="🛡 NETGUARD",
            font=("Segoe UI",26,"bold"),
            text_color="#3B82F6"
        ).pack()

        ctk.CTkLabel(
            header,
            text="Security Notification",
            font=("Segoe UI",14),
            text_color="gray70"
        ).pack()

        ctk.CTkLabel(
            container,
            text=icon,
            font=("Segoe UI Emoji", 72)
        ).pack()

        ctk.CTkLabel(
            container,
            text=title,
            font=("Segoe UI", 26, "bold")
        ).pack(pady=(15, 8))

        ctk.CTkLabel(
            container,
            text=message,
            wraplength=520,
            justify="center",
            font=("Segoe UI", 15)
        ).pack(pady=(0,25))