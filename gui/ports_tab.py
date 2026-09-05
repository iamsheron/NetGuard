import customtkinter as ctk
from datetime import datetime
from gui import theme
from gui.port_scanner import scan_ports, get_port_risk
from core import shared_state


class PortsTab(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(
            parent,
            fg_color="transparent"
        )

        self.current_device = None

        self.build_ui()

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="🔌 Port Security",
            font=("Segoe UI", 18, "bold")
        )

        title.pack(
            anchor="w",
            pady=(5, 4)
        )

        self.device_label = ctk.CTkLabel(
            self,
            text="No device selected",
            font=("Segoe UI", 12)
        )

        self.device_label.pack(
            anchor="w",
            pady=(0, 12)
        )

        self.scan_btn = ctk.CTkButton(
            self,
            text="🔎 Scan Ports",
            height=38,
            command=self.start_scan
        )

        self.scan_btn.pack(
            fill="x",
            pady=(0, 12)
        )

        self.status_label = ctk.CTkLabel(
            self,
            text="No port scan performed yet.",
            text_color="gray"
        )

        self.status_label.pack(
            anchor="w",
            pady=(0, 10)
        )

        self.results_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=theme.PANEL,
            corner_radius=12
        )

        self.results_frame.pack(
            fill="both",
            expand=True
        )

    # ==========================================
    # DEVICE
    # ==========================================

    def show_device(self, device):

        self.current_device = device

        ip = device.get("ip", "Unknown")
        name = device.get(
            "device_name",
            "Unknown Device"
        )

        self.device_label.configure(
            text=f"{name}\n{ip}"
        )

        self.clear_results()

        self.status_label.configure(
            text="No port scan performed yet."
        )

    # ==========================================
    # CLEAR
    # ==========================================

    def clear_results(self):

        for widget in self.results_frame.winfo_children():
            widget.destroy()

    # ==========================================
    # SCAN
    # ==========================================

    def start_scan(self):

        if not self.current_device:
            return

        ip = self.current_device.get("ip")

        if not ip:
            self.status_label.configure(
                text="❌ Device has no IP address."
            )
            return

        self.scan_btn.configure(
            state="disabled",
            text="🔄 Scanning..."
        )

        self.status_label.configure(
            text=f"Scanning {ip}..."
        )

        self.clear_results()

        self.after(
            100,
            lambda: self.run_scan(ip)
        )

    def run_scan(self, ip):

        try:

            results = scan_ports(ip)

            self.show_results(results)

        except Exception as e:

            self.status_label.configure(
                text=f"❌ Scan failed: {e}"
            )

        finally:

            self.scan_btn.configure(
                state="normal",
                text="🔄 Scan Again"
            )

    # ==========================================
    # RESULTS
    # ==========================================

    def show_results(self, results):

        self.clear_results()

        if not results:
            if self.current_device:
                self.current_device["open_ports"] = []

            self.status_label.configure(
                text=(
                    "✓ Scan complete — "
                    "no common open ports detected."
                )
            )

            return

        # ==========================================
        # RISK COUNTS
        # ==========================================

        low_count = 0
        review_count = 0
        high_count = 0

        processed_results = []

        for result in results:

            port = result["port"]

            service, risk = get_port_risk(port)

            if risk == "LOW":
                low_count += 1

            elif risk == "HIGH":
                high_count += 1

            else:
                review_count += 1

            processed_results.append({
                "port": port,
                "service": service,
                "state": "OPEN",
                 "risk": risk
            })
# ==========================================
# SAVE RESULTS TO CURRENT DEVICE
# ==========================================

        if self.current_device:

            self.current_device["open_ports"] = processed_results

    # ==========================================
    # SUMMARY
    # ==========================================

        summary = ctk.CTkFrame(
            self.results_frame,
            fg_color=theme.CARD,
            corner_radius=12
        )

        summary.pack(
            fill="x",
            pady=(0, 10)
        )

        ctk.CTkLabel(
            summary,
            text=f"🔌 {len(processed_results)} Open Ports",
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 4)
        )

        ctk.CTkLabel(
            summary,
            text=(
                f"🟢 {low_count} Low   "
                f"🟡 {review_count} Review   "
                f"🔴 {high_count} High"
            ),
            font=("Segoe UI", 12)
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 12)
        )

    # ==========================================
    # TIMESTAMP
    # ==========================================

        self.status_label.configure(
            text=(
                "✓ Scan complete\n"
                f"Scanned: "
                f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
            )
        )

    # ==========================================
    # TABLE HEADER
    # ==========================================

        header = ctk.CTkFrame(
            self.results_frame,
            fg_color="#1F2937",
            corner_radius=8
         )

        header.pack(
            fill="x",
            pady=(0, 6)
        )

        self.add_header(header, "PORT", 50)
        self.add_header(header, "SERVICE", 90)
        self.add_header(header, "STATE", 70)
        self.add_header(header, "RISK", 80)

    # ==========================================
    # PORT RESULTS
    # ==========================================

        for result in processed_results:

            row = ctk.CTkFrame(
                self.results_frame,
                fg_color=theme.CARD,
                corner_radius=8
            )

            row.pack(
                fill="x",
                pady=3
            )

            self.add_cell(
                row,
                str(result["port"]),
                50
            )

            self.add_cell(
                row,
                result["service"],
                90
            )

            self.add_cell(
                row,
                "🟢 OPEN",
                70
            )

            risk = result["risk"]

            if risk == "LOW":
                risk_text = "🟢 LOW"

            elif risk == "HIGH":
                risk_text = "🔴 HIGH"

            else:
                risk_text = "🟡 REVIEW"

            self.add_cell(
                row,
                risk_text,
                80
            )
    # ==========================================
    # UI HELPERS
    # ==========================================

    def add_header(self, parent, text, width):

        label = ctk.CTkLabel(
            parent,
            text=text,
            width=width,
            font=("Segoe UI", 11, "bold"),
            text_color="white"
        )

        label.pack(
            side="left",
            padx=5,
            pady=8
        )

    def add_cell(self, parent, text, width):

        label = ctk.CTkLabel(
            parent,
            text=text,
            width=width,
            anchor="w"
        )

        label.pack(
            side="left",
            padx=5,
            pady=8
        )