import customtkinter as ctk


class GeneralTab(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.labels = {}

        fields = [
            "Device Name",
            "IP Address",
            "MAC Address",
            "Vendor",
            "Device Type",
            "Status",
            "First Seen",
            "Last Seen"
        ]

        for field in fields:

            row = ctk.CTkFrame(
                self,
                fg_color="transparent"
            )

            row.pack(fill="x", pady=4)

            ctk.CTkLabel(
                row,
                text=field + ":",
                width=120,
                anchor="w",
                font=("Segoe UI", 13, "bold")
            ).pack(side="left")

            value = ctk.CTkLabel(
                row,
                text="-",
                anchor="w"
            )

            value.pack(side="left")

            self.labels[field] = value

    def show_device(self, device):

        self.labels["Device Name"].configure(text=device["device_name"])
        self.labels["IP Address"].configure(text=device["ip"])
        self.labels["MAC Address"].configure(text=device["mac"])
        self.labels["Vendor"].configure(text=device["vendor"])
        self.labels["Device Type"].configure(text=device["device_type"])
        self.labels["Status"].configure(text=device["status"])
        self.labels["First Seen"].configure(text=device["first_seen"])
        self.labels["Last Seen"].configure(text=device["last_seen"])