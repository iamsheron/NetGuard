import customtkinter as ctk
from gui import theme
import threading
from services.os_detector import OSDetector
from database import update_operating_system


class SecurityTab(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        # -------- Security Title --------

        ctk.CTkLabel(
            self,
            text="🛡 Security",
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", pady=(0,15))

        self.os_label = self.add_row(
            "Operating System",
            "Unknown"
        )

        self.port_label = self.add_row(
            "Open Ports",
            "Not Scanned"
        )

        self.risk_label = self.add_row(
            "Risk Score",
            "Low"
        )

        self.rogue_label = self.add_row(
            "Rogue Device",
            "No"
        )
        self.detect_os_btn = ctk.CTkButton(
            self,
            text="🌐 Detect Operating System",
            command=self.detect_os,
            height=38
            )

        self.detect_os_btn.pack(
            fill="x",
            pady=(20, 0)
            )

    def add_row(self, title, value):

        row = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        row.pack(fill="x", pady=5)

        ctk.CTkLabel(
            row,
            text=title + ":",
            width=140,
            anchor="w",
            font=("Segoe UI",13,"bold")
        ).pack(side="left")

        lbl = ctk.CTkLabel(
            row,
            text=value
        )

        lbl.pack(side="left")

        return lbl

    def show_device(self, device):

        self.current_device = device

        self.os_label.configure(
        text=device["operating_system"]
        )

        self.port_label.configure(
        text="Not Scanned"
        )

        self.risk_label.configure(
        text="Low"
        )

        self.rogue_label.configure(
        text="No"
        )

    def detect_os(self):
    
        if not hasattr(self, "current_device"):
             return
    
        self.detect_os_btn.configure(
            text="⏳ Detecting...",
            state="disabled"
            )
    
        thread = threading.Thread(
            target=self.detect_os_worker,
            daemon=True
            )
    
        thread.start()
    
    def detect_os_worker(self):
    
        detector = OSDetector()
    
        ip = self.current_device["ip"]
    
        os_name = detector.detect(ip)
    
        update_operating_system(
            self.current_device["mac"],
            os_name
            )
    
        self.after(
            0,
            lambda: self.detect_os_finished(os_name)
            )
    

    def detect_os_finished(self, os_name):

        self.current_device["operating_system"] = os_name
    
        self.os_label.configure(text=os_name)
    
        self.detect_os_btn.configure(
            text="🌐 Detect Operating System",
            state="normal"
            )