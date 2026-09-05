import customtkinter as ctk
from gui import theme
from gui.general_tab import GeneralTab
from gui.security_tab import SecurityTab
from gui.ports_tab import PortsTab
from database import trust_device,update_security_status
from database import mark_as_rogue



class DeviceDetailsPanel(ctk.CTkScrollableFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=theme.PANEL,
            corner_radius=18,
            width=400
        )

        self.configure(width=400)

       

        self.build_ui()

    # ---------------------------------

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="🛡 Device Details",
            font=("Segoe UI", 22, "bold")
        )

        title.pack(anchor="w", padx=20, pady=(20,15))

        self.trust_btn = ctk.CTkButton(
            self,
            text="🟢 Trust Device",
            command=self.trust_selected_device
        )

        self.trust_btn.pack(
            fill="x",
            padx=20,
            pady=15
        )
        self.rogue_btn = ctk.CTkButton(
            self,
            text="🚫 Mark as Rogue",
            width=360,
            height=27,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.mark_selected_rogue
        )

        self.rogue_btn.pack(pady=(8, 12))

        # ==========================
        # Tab Buttons
# ==========================

        tab_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        tab_frame.pack(fill="x", padx=20, pady=(0,15))

        self.general_btn = ctk.CTkButton(
            tab_frame,
            text="🖥 General",
            width=110,
            command=self.show_general_tab
            )

        self.general_btn.pack(side="left", padx=(0,8))

        self.security_btn = ctk.CTkButton(
            tab_frame,
            text="🛡 Security",
            width=110,
            command=self.show_security_tab
            )

        self.security_btn.pack(side="left", padx=8)

        self.ports_btn = ctk.CTkButton(
            tab_frame,
            text="🌐 Ports",
            width=110,
            command=self.show_ports_tab
        )

        self.ports_btn.pack(side="left", padx=8)
        # ==========================
        # Tab Container
        # ==========================

        self.tab_container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.tab_container.pack(
            fill="both",
            expand=True,
            padx=20
        )
        # ==========================
        # Tabs
        # ==========================

        self.general_tab = GeneralTab(self.tab_container)

        self.general_tab.pack(
            fill="both",
            expand=True
        )
        self.security_tab = SecurityTab(self.tab_container)
        self.ports_tab = PortsTab(self.tab_container)

        #info = ctk.CTkFrame(self, fg_color="transparent")
        #info.pack(fill="x", padx=20)

       
        # ----------------------------
        # Security Section
        # ----------------------------

       

      
    # ---------------------------------

    

    # ---------------------------------
        
    def show_device(self, device):

        self.current_device = device

        self.general_tab.show_device(device)
        self.security_tab.show_device(device)
        self.ports_tab.show_device(device)

       
   
    def show_general_tab(self):

        self.security_tab.pack_forget()
        self.ports_tab.pack_forget()

        self.general_tab.pack(
        fill="both",
        expand=True
    )


    def show_security_tab(self):

        self.general_tab.pack_forget()
        self.ports_tab.pack_forget()

        self.security_tab.pack(
        fill="both",
        expand=True
    )


    def show_ports_tab(self):

       self.general_tab.pack_forget()
       self.security_tab.pack_forget()

       self.ports_tab.pack(
            fill="both",
            expand=True
        )

    def trust_selected_device(self):

        if not hasattr(self, "current_device"):
            return

        trust_device(
            self.current_device["mac"],
            self.current_device["device_name"],
            self.current_device["vendor"]
        )

        

        update_security_status(
            self.current_device["mac"],
            "TRUSTED"
        )

        self.current_device["security_status"] = "TRUSTED"
        self.show_device(self.current_device)
        self.app.show_dashboard()
        self.app.show_security_center()

    def mark_selected_rogue(self):

        if not hasattr(self, "current_device"):
            return

        mark_as_rogue(
            self.current_device["mac"]
        )

        self.current_device["security_status"] = "ROGUE"

        self.show_device(self.current_device)

        self.app.show_dashboard()
        self.app.show_security_center()
