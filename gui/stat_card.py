import customtkinter as ctk
from gui import theme


class StatCard(ctk.CTkFrame):

    def __init__(self, parent, title, icon, value="0", color="#3B82F6"):
        super().__init__(
            parent,
            fg_color=theme.PANEL,
            corner_radius=18,
            height=120
        )

        self.pack_propagate(False)

        self.color = color

        # -------------------------
        # Icon
        # -------------------------

        self.icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=("Segoe UI Emoji", 22)
        )
        self.icon_label.pack(pady=(12, 2))

        # -------------------------
        # Value
        # -------------------------

        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=("Segoe UI", 30, "bold"),
            text_color=color
        )
        self.value_label.pack()

        # -------------------------
        # Title
        # -------------------------

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 14)
        )
        self.title_label.pack(pady=(2, 10))

    # -------------------------
    # Update Value
    # -------------------------

    def set_value(self, value):
        self.value_label.configure(text=str(value))