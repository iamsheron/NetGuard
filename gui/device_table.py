import customtkinter as ctk
from gui import theme


class DeviceTable(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.PANEL, corner_radius=15)

        self.pack(fill="both", expand=True)

        self.devices = []
        self.on_device_selected = None
        self.selected_row = None

        self.create_header()

        self.rows_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )

        self.rows_frame.pack(fill="both", expand=True)

    # -------------------------------------

    def create_header(self):

        header = ctk.CTkFrame(
            self,
            fg_color=theme.CARD,
            height=45,
            corner_radius=10
        )

        header.pack(fill="x", padx=10, pady=(10,5))
        header.pack_propagate(False)

        columns = [
            ("Device", 170),
            ("IP Address", 170),
            ("Vendor", 180),
            ("Type", 130),
            ("Status", 100)
        ]
        for text, width in columns:
        
            lbl = ctk.CTkLabel(
                header,
                text=text,
                width=width,
                anchor="w",
                font=("Segoe UI", 14, "bold")
            )
        
            lbl.pack(side="left", padx=8)

    def get_status_style(self, device):

        if device["status"] == "Offline":
            return "⚪ OFFLINE", "#6B7280"

        security = device.get("security_status", "NEW")

        if security == "TRUSTED":
            return "🟢 TRUSTED", "#22C55E"

        elif security == "ROGUE":
            return "🔴 ROGUE", "#EF4444"

        elif security == "NEW":
            return "🟡 NEW", "#F59E0B"

        else:
            return "⚪ UNKNOWN", "#6B7280"

       

    # -------------------------------------

    def clear(self):

        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        self.selected_row = None

    # -------------------------------------

    def load_devices(self, devices):

        self.devices = devices

        self.clear()
        self.rows = []

        for device in devices:

            row = ctk.CTkFrame(
                self.rows_frame,
                fg_color=theme.PANEL,
                height=40,
                corner_radius=8
            )
            row.device = device
            self.rows.append((row, device))

            row.pack(fill="x", padx=10, pady=3)

            row.bind(
                "<Button-1>",
                lambda e, d=device, r=row: self.select_device(d, r)
            )
            status_text, status_color = self.get_status_style(device)


            values = [

                device["device_name"],
                device["ip"],
                device["vendor"],
                device["device_type"],
                status_text

            ]

            widths = [170,170,180,130,100]

            for index, (value, width) in enumerate(zip(values, widths)):

                color = None

                if index == 4:

                 if "NEW" in value:
                    color = "#F59E0B"      # Orange

                elif "TRUSTED" in value:
                    color = "#22C55E"      # Green

                elif "ROGUE" in value:
                    color = "#EF4444"      # Red

                elif "OFFLINE" in value:
                    color = "#A3A3A3"      # Gray         # Status column

                if index == 4:

                    lbl = ctk.CTkLabel(
                        row,
                        text=status_text,
                        width=100,
                        corner_radius=8,
                        fg_color=status_color,
                        text_color="white",
                        font=("Segoe UI", 11, "bold")
                    )

                else:

                    lbl = ctk.CTkLabel(
                        row,
                        text=str(value),
                        width=width,
                        anchor="w"
                    )
                
                lbl.pack(side="left", padx=8)

                lbl.bind(
                    "<Button-1>",
                    lambda e, d=device, r=row: self.select_device(d, r)
                )
    def select_device(self, device, row=None):

        # Clear previous selection safely
        if self.selected_row:
            try:
                if self.selected_row.winfo_exists():
                     self.selected_row.configure(fg_color=theme.PANEL)
            except:
                pass

        # Highlight new selection
        if row:
            row.configure(fg_color=("#DCEEFF", "#2F5D8C"))
            self.selected_row = row

        # Notify dashboard
        if self.on_device_selected:
            self.on_device_selected(device)

    def select_first_device(self):

        if self.rows:
            row, device = self.rows[0]
            self.select_device(device, row)