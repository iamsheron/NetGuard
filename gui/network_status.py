import customtkinter as ctk


class NetworkStatus(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="transparent"
        )

        self.build_ui()

    def build_ui(self):

        # Title
        ctk.CTkLabel(
            self,
            text="🌐 Network Status",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(0,15))

        self.status = self.add_row(
            "Protection",
            "Protected"
        )

        self.online = self.add_row(
            "Online Devices",
            "0"
        )

        self.offline = self.add_row(
            "Offline Devices",
            "0"
        )

        self.last_scan = self.add_row(
            "Last Scan",
            "Never"
        )

        self.scan_time = self.add_row(
            "Scan Duration",
            "0 sec"
        )

    def add_row(self, title, value):

        row = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        row.pack(fill="x", pady=6)

        ctk.CTkLabel(
            row,
            text=title,
            width=150,
            anchor="w",
            font=("Segoe UI",13,"bold")
        ).pack(side="left")

        label = ctk.CTkLabel(
            row,
            text=value
        )

        label.pack(side="left")

        return label

    def update_status(
        self,
        online,
        offline,
        last_scan,
        duration
    ):

        self.online.configure(text=str(online))
        self.offline.configure(text=str(offline))
        self.last_scan.configure(text=last_scan)
        self.scan_time.configure(text=duration)