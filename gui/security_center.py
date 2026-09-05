import customtkinter as ctk
import os
from datetime import datetime
from tkinter import filedialog, messagebox
from gui import theme
from gui.network_status import NetworkStatus
from core import shared_state
from services.alert_manager import AlertManager
from services.risk_analyzer import analyze_device
from gui.scan_activity_graph import ScanActivityGraph
from gui.settings_page import SettingsPage

class SecurityCenterPage(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=theme.BACKGROUND)

        self.app = app

        self.alert_manager = AlertManager()

        self.pack(fill="both", expand=True)

        self.build_ui()

        self.load_shared_data()

       

       

    def build_ui(self):

    # ==========================
    # Header
    # ==========================

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=25,
            pady=(20, 15)
        )

        ctk.CTkLabel(
            header,
            text="🛡 Security Center",
            font=("Segoe UI", 30, "bold")
        ).pack(side="left")

        back_btn = ctk.CTkButton(
            header,
            text="← Dashboard",
            width=140,
            command=self.back_dashboard
        )

        back_btn.pack(side="right")

# ==========================
    # Main Content
    # ==========================

        content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        content.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 10)
        )

    # Three rows:
    #
    # Row 0 = four security cards
    # Row 1 = network topology
    # Row 2 = toolbar

       

        content.grid_rowconfigure(
            0,
            weight=1
        )

        content.grid_columnconfigure(
            0,
            weight=1
        )

        content.grid_columnconfigure(
            1,
            weight=1
        )

    # ==========================
    # Four Security Cards
    # ==========================

        cards = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )

        cards.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=0,
            pady=0

        )

        cards.grid_rowconfigure(
            0,
            weight=1
        )

        cards.grid_rowconfigure(
            1,
            weight=1
        )

        cards.grid_columnconfigure(
            0,
            weight=1
        )

        cards.grid_columnconfigure(
            1,
            weight=1
        )
        

        

    # ==========================
    # Network Status
    # ==========================

        status_card = ctk.CTkFrame(
            cards,
            fg_color=theme.PANEL,
            corner_radius=18
        )

        status_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 6),
            pady=(0, 6)
        )

        self.network_status = NetworkStatus(
            status_card
        )

        self.network_status.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

    # ==========================
    # Recommended Actions
    # ==========================

        self.threat_card = self.create_card(
            cards,
            "🛡 Recommended Actions"
        )

        self.threat_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(6, 0),
            pady=(0, 6)
        )

        self.risk_frame = ctk.CTkScrollableFrame(
            self.threat_card,
            fg_color="transparent"
        )

        self.risk_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

    # ==========================
    # Recent Alerts
    # ==========================

        self.alert_card = self.create_card(
            cards,
            "Recent Alerts"
        )

        self.alert_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(0, 6),
            pady=(6, 0)
        )

        self.alerts_frame = ctk.CTkScrollableFrame(
            self.alert_card,
            fg_color="transparent"
        )

        self.alerts_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

    # ==========================
    # Scan Activity
    # ==========================

        self.activity_card = ctk.CTkFrame(
            cards,
            fg_color="transparent"
        )

        self.activity_card.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(6, 0),
            pady=(6, 0)
        )

        self.scan_activity_graph = ScanActivityGraph(
            self.activity_card,
            shared_state,
            theme
        )

        self.scan_activity_graph.pack(
            fill="both",
            expand=True
        )

    # ==========================
    
    # ==========================
    # Bottom Toolbar
    # ==========================

        toolbar = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )

        toolbar.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(10, 0)
        )

        buttons = [
            ("Refresh", self.refresh_security_center),
            ("Export Reports", self.export_report),
            ("Reports", self.open_reports),
            ("Settings", self.open_settings)
        ]

        for text, command in buttons:

            ctk.CTkButton(
                toolbar,
                text=text,
                width=170,
                command=command
            ).pack(
                side="left",
                padx=8
            )

    # ==========================
    # Alert Refresh
    # ==========================

        self.start_alert_refresh()
   
    def create_card(self, parent, title):

        card = ctk.CTkFrame(
            parent,
            fg_color=theme.PANEL,
            corner_radius=18
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", padx=20, pady=15)

        return card

    def load_alerts(self):

        for widget in self.alerts_frame.winfo_children():
            widget.destroy()

        alerts = shared_state.alerts

        if not alerts:

            ctk.CTkLabel(
                self.alerts_frame,
                text="No security events detected.",
                text_color="gray70",
                font=("Segoe UI", 13)
            ).pack(
               pady=30
            )

            return

        for alert in alerts[:10]:

            if alert["level"] == "CRITICAL":
                color = "#DC2626"

            elif alert["level"] == "WARNING":
                color = "#F59E0B"

            else:
                color = "#3B82F6"

            alert_frame = ctk.CTkFrame(
                self.alerts_frame,
                fg_color=theme.CARD,
                corner_radius=10
            )

            alert_frame.pack(
                fill="x",
                padx=5,
                pady=4
            )

            ctk.CTkLabel(
                alert_frame,
                text=alert["title"],
                font=("Segoe UI", 13, "bold"),
                text_color=color,
                anchor="w"
            ).pack(
                anchor="w",
                padx=12,
                pady=(10,3)
            )

            ctk.CTkLabel(
                alert_frame,
                text=alert["message"],
                font=("Segoe UI", 11),
                wraplength=400,
                anchor="w",
                justify="left"
            ).pack(
                anchor="w",
                padx=12,
                pady=3
            )

            ctk.CTkLabel(
                alert_frame,
                text=alert["time"],
                font=("Segoe UI", 10),
                text_color="gray60"
            ).pack(
                anchor="w",
                padx=12,
                pady=(3,10)
            )
        self.alerts_frame.after(
            10,
            lambda: self.alerts_frame._parent_canvas.yview_moveto(0)
        )

    def back_dashboard(self):
        self.app.show_dashboard()

    # ==================================================
    # SECURITY CENTER ACTIONS
    # ==================================================

    def refresh_security_center(self):
        """Refresh the information already available in shared state.

        This deliberately does NOT start a new network scan.
        """
        try:
            self.load_shared_data()

            # Refresh the network-status widget if it exposes its own
            # refresh/update method; otherwise load_shared_data already
            # updated it.
            self.update_idletasks()

            messagebox.showinfo(
                "NETGUARD",
                "Security Center refreshed successfully."
            )
        except Exception as error:
            messagebox.showerror(
                "Refresh Error",
                f"Could not refresh Security Center.\\n\\n{error}"
            )

    def _build_report_text(self):
        """Build a compact snapshot of the current Security Center state."""
        devices = list(shared_state.devices or [])
        alerts = list(shared_state.alerts or [])

        lines = [
            "NETGUARD SECURITY REPORT",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "NETWORK SUMMARY",
            "-" * 60,
            f"Online devices : {shared_state.online_devices}",
            f"Offline devices: {shared_state.offline_devices}",
            f"Last scan      : {shared_state.last_scan}",
            f"Scan duration  : {shared_state.scan_duration}",
            "",
            "DEVICES",
            "-" * 60,
        ]

        if devices:
            for index, device in enumerate(devices, 1):
                lines.extend([
                    f"{index}. {device.get('device_name', 'Unknown Device')}",
                    f"   IP       : {device.get('ip', 'Unknown')}",
                    f"   MAC      : {device.get('mac', 'Unknown')}",
                    f"   Type     : {device.get('device_type', 'Unknown')}",
                    f"   Vendor   : {device.get('vendor', 'Unknown')}",
                    f"   Trusted  : {device.get('is_trusted', False)}",
                    f"   Status   : {device.get('status', 'Unknown')}",
                    "",
                ])
        else:
            lines.append("No devices available.")
            lines.append("")

        lines.extend([
            "RECENT ALERTS",
            "-" * 60,
        ])

        if alerts:
            for alert in alerts[:20]:
                lines.extend([
                    f"[{alert.get('level', 'INFO')}] {alert.get('title', 'Security Event')}",
                    f"{alert.get('message', '')}",
                    f"Time: {alert.get('time', '')}",
                    "",
                ])
        else:
            lines.append("No security events detected.")
            lines.append("")

        return "\n".join(lines)

    def export_report(self):
        """Export the current Security Center snapshot as a PDF."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.enums import TA_CENTER
            from xml.sax.saxutils import escape

            reports_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "reports"
            )
            os.makedirs(reports_dir, exist_ok=True)

            filename = (
                f"netguard_security_report_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            default_path = os.path.join(reports_dir, filename)

            save_path = filedialog.asksaveasfilename(
                title="Export NETGUARD Security Report",
                initialdir=reports_dir,
                initialfile=filename,
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")]
            )

            if not save_path:
                return

            styles = getSampleStyleSheet()
            title_style = styles["Title"]
            title_style.alignment = TA_CENTER
            body_style = styles["BodyText"]
            body_style.fontName = "Helvetica"
            body_style.fontSize = 9
            body_style.leading = 12

            doc = SimpleDocTemplate(
                save_path,
                pagesize=A4,
                rightMargin=15 * mm,
                leftMargin=15 * mm,
                topMargin=15 * mm,
                bottomMargin=15 * mm,
            )

            story = [
                Paragraph("NETGUARD SECURITY REPORT", title_style),
                Spacer(1, 8),
            ]

            for line in self._build_report_text().splitlines():
                if line.strip():
                    story.append(
                        Paragraph(
                            escape(line).replace("  ", "&nbsp;&nbsp;"),
                            body_style
                        )
                    )
                else:
                    story.append(Spacer(1, 5))

            doc.build(story)

            messagebox.showinfo(
                "Report Exported",
                f"Security report exported successfully.\\n\\n{save_path}"
            )

        except ImportError:
            messagebox.showerror(
                "Export Error",
                "The PDF reporting library is not available."
            )
        except Exception as error:
            messagebox.showerror(
                "Export Error",
                f"Could not export the security report.\\n\\n{error}"
            )

    def open_reports(self):
        """Open the reports folder and show the latest report."""
        try:
            reports_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "reports"
            )
            os.makedirs(reports_dir, exist_ok=True)

            pdfs = [
                os.path.join(reports_dir, name)
                for name in os.listdir(reports_dir)
                if name.lower().endswith(".pdf")
            ]
            pdfs.sort(key=os.path.getmtime, reverse=True)

            if not pdfs:
                messagebox.showinfo(
                    "Reports",
                    "No exported security reports are available yet.\\n\\n"
                    "Use 'Export Reports' to create the first report."
                )
                return

            latest = pdfs[0]

            # Open the latest report with the operating system's
            # default PDF viewer.
            os.startfile(latest)

        except Exception as error:
            messagebox.showerror(
                "Reports Error",
                f"Could not open the reports.\\n\\n{error}"
            )

    def open_settings(self):
        self.app.show_settings()

    def load_shared_data(self):

        self.network_status.update_status(
            online=shared_state.online_devices,
            offline=shared_state.offline_devices,
            last_scan=shared_state.last_scan,
            duration=shared_state.scan_duration
        )

        self.load_alerts()
        self.load_recommended_actions()

    def start_alert_refresh(self):
        self.load_alerts()

        self.after(
            1000,
            self.start_alert_refresh
        )

    def load_recommended_actions(self):

        for widget in self.risk_frame.winfo_children():
            widget.destroy()

        devices = shared_state.devices

        if not devices:

            ctk.CTkLabel(
                self.risk_frame,
                text="No devices available.",
                text_color="gray70",
                font=("Segoe UI", 13)
            ).pack(pady=30)

            return

        analyses = []

        for device in devices:

            analysis = analyze_device(device)

            analyses.append(
                (device, analysis)
            )

        # Highest-risk devices first
        analyses.sort(
            key=lambda item: item[1]["score"],
            reverse=True
        )

        # Show the most important findings
        for device, analysis in analyses[:4]:

            self.create_risk_item(
                device,
                analysis
            )

    def create_risk_item(self, device, analysis):

        score = analysis["score"]
        level = analysis["level"]

        if level == "CRITICAL":
            icon = "🔴"
            color = "#DC2626"

        elif level == "HIGH":
            icon = "🟠"
            color = "#EA580C"

        elif level == "MEDIUM":
            icon = "🟡"
            color = "#F59E0B"

        else:
            icon = "🟢"
            color = "#16A34A"

        frame = ctk.CTkFrame(
            self.risk_frame,
            fg_color=theme.CARD,
            corner_radius=12
        )

        frame.pack(
            fill="x",
            pady=4
        )

        name = device.get(
            "device_name",
            "Unknown Device"
        )

        ip = device.get(
            "ip",
            "Unknown IP"
        )

        ctk.CTkLabel(
            frame,
            text=f"{icon} {name}",
            font=("Segoe UI", 13, "bold"),
            text_color=color,
            anchor="w"
        ).pack(
            anchor="w",
            padx=12,
            pady=(10, 2)
        )

        ctk.CTkLabel(
            frame,
            text=f"{ip}   •   Risk Score: {score}/100 ({level})",
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        ).pack(
            anchor="w",
            padx=12,
            pady=2
        )

         # Why flagged
        ctk.CTkLabel(
            frame,
            text="Why flagged:",
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        ).pack(
            anchor="w",
            padx=12,
            pady=(7, 2)
        )

        for finding in analysis["findings"][:3]:

            ctk.CTkLabel(
                frame,
                text=f"• {finding}",
                font=("Segoe UI", 10),
                anchor="w",
                justify="left",
                wraplength=360
            ).pack(
                anchor="w",
                padx=18,
                pady=1
            )

           # Recommended action
        ctk.CTkLabel(
            frame,
            text="Recommended:",
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        ).pack(
            anchor="w",
            padx=12,
            pady=(7, 2)
        )

        ctk.CTkLabel(
            frame,
            text=f"• {analysis['actions'][0]}",
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
            wraplength=360
        ).pack(
            anchor="w",
            padx=18,
            pady=(1, 10)
        )