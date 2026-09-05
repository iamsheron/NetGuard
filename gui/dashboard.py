import customtkinter as ctk
from gui import theme
from gui.device_table import DeviceTable
from stage1_scan import scan_network, process_devices
from database import create_database, mark_all_devices_offline,get_offline_device_count,get_device_counts
import threading
from gui.stat_card import StatCard
from gui.device_details_panel import DeviceDetailsPanel
from services.alert_manager import AlertManager
from services.notification_manager import NotificationManager
from gui.modern_dialog import ModernDialog
from core import shared_state
import time
import threading
from arp_detector import ARPSpoofDetector
from pdf_report import generate_security_report
from tkinter import filedialog

alert_manager = AlertManager()
notification_manager = NotificationManager()


class DashboardPage(ctk.CTkFrame):

    def show_device_details(self, device):

       self.details_panel.show_device(device)

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=theme.BACKGROUND)

        self.app = app
        self.pack(fill="both", expand=True, padx=25, pady=20)

        self.build_ui()
        self.arp_detector = ARPSpoofDetector()
        self.arp_monitor_started = False

    def build_ui(self):

        # ===========================
        # Title
        # ===========================

        title = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=("Segoe UI", 30, "bold")
        )
        title.pack(anchor="w", pady=(0,20))

        # ===========================
        # Statistics
        # ===========================

        self.stats_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.stats_frame.pack(fill="x")


        self.online_card = StatCard(
            self.stats_frame,
            "Online Devices",
            "🟢",
            "0",
            "#22C55E"
        )
        self.online_card.pack(side="left", expand=True, fill="x", padx=8)

        self.offline_card = StatCard(
            self.stats_frame,
            "Offline Devices",
            "🔴",
            "0",
            "#EF4444"
        )
        self.offline_card.pack(side="left", expand=True, fill="x", padx=8)

        self.alert_card = StatCard(
            self.stats_frame,
            "Alerts",
            "🚨",
            "0",
            "#F59E0B"
        )
        self.alert_card.pack(side="left", expand=True, fill="x", padx=8)

        self.rogue_card = StatCard(
            self.stats_frame,
            "Rogue Devices",
            "🛡",
            "0",
            "#3B82F6"
        )
        self.rogue_card.pack(side="left", expand=True, fill="x", padx=8)

        
        # ===========================
        # Toolbar
        # ===========================

        toolbar = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        toolbar.pack(fill="x", pady=25)

        self.refresh_btn = ctk.CTkButton(
             toolbar,
             text="🔄 Refresh Scan",
             width=170,
             command=self.refresh_scan
        )

        self.refresh_btn.pack(side="left")

        self.pdf_btn = ctk.CTkButton(
            toolbar,
            text="📄 Security Report",
            width=170,
            command=self.generate_pdf_report
        )

        self.pdf_btn.pack(side="left", padx=(10, 0))

        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Search Device...",
            width=300
        )

        self.search_entry.pack(side="right")

        self.search_entry.bind(
            "<KeyRelease>",
            self.search_devices
        )

        # ===========================
        # Device Frame
        # ===========================

         # ===========================
         # Device Monitor
         # ===========================

        # ===========================
        # Main Content
        # ===========================

        main_content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        main_content.pack(fill="both",expand=True)

        # ---------------------------
        # Left Panel
        # ---------------------------

        left_panel = ctk.CTkFrame(
            main_content,
            fg_color=theme.PANEL,
            corner_radius=18
        )

        left_panel.pack(side="left", fill="both", expand=True)

        title_frame = ctk.CTkFrame(
            left_panel,
            fg_color="transparent"
        )

        title_frame.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            title_frame,
            text="Device Monitor",
            font=("Segoe UI", 20, "bold")
        ).pack(side="left")

        self.device_table = DeviceTable(left_panel)
        self.device_table.on_device_selected = self.show_device_details

        # ---------------------------
        # Right Panel
        # ---------------------------

        self.details_panel =  DeviceDetailsPanel(main_content)

        self.details_panel.pack(
            side="right",
            fill="both",
            padx=(15, 0)
            
        )
        
        # ===========================
        # Security Center
        # ===========================

        security = ctk.CTkFrame(
            self,
            fg_color=theme.PANEL,
            corner_radius=18
        )
        security.pack(fill="x", pady=20)
       
        # Header
        header = ctk.CTkFrame(
            security,
            fg_color="transparent"
        )

        header.pack(fill="x", padx=20, pady=(15,10))

        ctk.CTkLabel(
            header,
            text="🛡 Security Center",
            font=("Segoe UI",20,"bold")
        ).pack(side="left",pady=5)

        self.open_security_btn = ctk.CTkButton(
            header,
            text="Open ➜",
            width=110,
            height=36,
            corner_radius=10,
            command=self.open_security_center
        )

        self.open_security_btn.pack(side="right",pady=5)

        ctk.CTkLabel(
            security,
            text="Network Protection • Threat Detection • Live Monitoring",
            font=("Segoe UI", 13),
            text_color="gray70"
        ).pack(anchor="w", padx=20, pady=(0, 18))

       

    def create_stat_card(self, title, value):

        card = ctk.CTkFrame(
            self.stats_frame,
            fg_color=theme.PANEL,
            corner_radius=18,
            height=110
        )

        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI",15)
        ).pack(pady=(18,5))

        ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI",28,"bold")
        ).pack()

        return card


    def search_devices(self, event=None):

        query = self.search_entry.get().strip().lower()

        # Nothing typed → show all devices
        if not query:
            self.device_table.load_devices(
                shared_state.devices
            )

            if shared_state.devices:
                self.device_table.select_first_device()

            return

        filtered_devices = []

        for device in shared_state.devices:

            searchable_values = [
                device.get("device_name", ""),
                device.get("ip", ""),
                device.get("mac", ""),
                device.get("vendor", ""),
                device.get("device_type", ""),
                device.get("security_status", ""),
            ]

            searchable_text = " ".join(
                str(value).lower()
                for value in searchable_values
            )

            if query in searchable_text:
                filtered_devices.append(device)

        self.device_table.load_devices(
            filtered_devices
        )

        if filtered_devices:
            self.device_table.select_first_device()
    
    def refresh_scan(self):

        self.refresh_btn.configure(
        text="⏳ Scanning...",
        state="disabled"
        )

        self.app.status_label.configure(text="🔄 Scanning Network...")
        thread = threading.Thread(
            target=self.scan_worker,
            daemon=True
        )

        thread.start()

    def generate_pdf_report(self):

        filename = filedialog.asksaveasfilename(
            parent=self,
            title="Save NetGuard Security Report",
            defaultextension=".pdf",
            filetypes=[
                ("PDF files", "*.pdf")
            ],
            initialfile="NetGuard_Security_Report.pdf"
        )

        if not filename:
            return

        try:

            devices = shared_state.devices
            alerts = shared_state.alerts

            online_devices = shared_state.online_devices
            offline_devices = shared_state.offline_devices

            rogue_devices = sum(
                1
                for device in devices
                if not device.get("is_trusted", True)
            )

            generate_security_report(
                filename=filename,
                devices=devices,
                alerts=alerts,
                online_devices=online_devices,
                offline_devices=offline_devices,
                rogue_devices=rogue_devices,
                last_scan=shared_state.last_scan,
                scan_duration=shared_state.scan_duration
            )

            print("✅ Security PDF generated:")
            print(filename)

            self.app.status_label.configure(
                text="📄 Security Report Generated"
            )

        except Exception as e:

            print("❌ PDF generation failed:")
            print(e)

            self.app.status_label.configure(
                text="❌ PDF Generation Failed"
            )

    def scan_worker(self):

        start_time = time.time()

        create_database()
        mark_all_devices_offline()

        
        result = scan_network()

        devices = process_devices(result)
        print(f"Found {len(devices)} devices")
        print(devices)

        self.start_arp_monitor()
        

        shared_state.devices = devices

        online, offline = get_device_counts()

        shared_state.online_devices = online
        shared_state.offline_devices = offline
        print("========== Shared State ==========")
        print("Online:", shared_state.online_devices)
        print("Offline:", shared_state.offline_devices)
        print("==================================")

    
        for device in devices:

            if device["is_new"]:

                alert = alert_manager.raise_alert(
                    level="INFO",
                    title="🚨 New Device",
                    message=f'{device["device_name"]} joined the network.',
                    device=device
                )

                notification_manager.notify(alert)
               

                self.after(
                    0,
                    lambda a=alert: ModernDialog(
                        self,
                        icon="🚨",
                        title=a["title"],
                        message=a["message"],
                        details=a["device"]
                    )
                )

            if not device["is_trusted"]:

                alert = alert_manager.raise_alert(
                    level="WARNING",
                    title="🚨 Rogue Device Detected",
                    message=f'{device["device_name"]} is NOT trusted.',
                    device=device
                )

                notification_manager.notify(alert)
               

                self.after(
                    0,
                    lambda a=alert: ModernDialog(
                        self,
                        icon="🚨",
                        title=a["title"],
                        message=a["message"],
                        details=a["device"]
                    )
                )  

        try:
            from datetime import datetime
            shared_state.last_scan = datetime.now().strftime("%H:%M:%S")
            duration = time.time() - start_time
            shared_state.scan_duration = f"{duration:.2f} sec"
            print("Updating dashboard...")
            self.after(0, lambda: self.update_dashboard(devices))
        except:
            pass

    def start_arp_monitor(self):

        if self.arp_monitor_started:
            return

        self.arp_monitor_started = True

        def monitor():

            print("🛡 Starting ARP security monitor...")

            # Build the initial baseline
            self.arp_detector.build_baseline(
                "192.168.1.0/24"
            )

            # Start continuous monitoring
            self.arp_detector.monitor()

        thread = threading.Thread(
            target=monitor,
            daemon=True
        )

        thread.start()

    def update_dashboard(self, devices):


       print("Entered update_dashboard")

       print(devices)

       print("Loading table...")

       self.device_table.load_devices(devices)

       print("Table loaded successfully")

       if not self.winfo_exists():
            return

       try:
            self.device_table.load_devices(devices)
       except:
            return
     
       if devices:
            self.device_table.select_first_device()

       online = len(devices)
       offline = get_offline_device_count()          
       alerts = len(alert_manager.get_alerts())
       self.alert_card.set_value(alerts)
       rogue = sum(
            1
            for d in devices
            if d.get("security_status") == "ROGUE"
        )
       shared_state.rogue_devices = rogue
       print("===== ROGUE DEBUG =====")
       for device in devices:
            print(device["device_name"], device["is_trusted"])
       print("Rogue Count:", rogue)
       print("=======================")
       self.online_card.set_value(online)
       self.offline_card.set_value(offline)
       self.alert_card.set_value(alerts)
       self.rogue_card.set_value(rogue)

       
      

       self.refresh_btn.configure(
            text="🔄 Refresh Scan",
            state="normal"
            )

       self.app.status_label.configure(text="✅ Scan Complete")
        
    def open_security_center(self):
        print("Security Center Coming Soon...")

    def open_security_center(self):
        self.app.show_security_center()
    