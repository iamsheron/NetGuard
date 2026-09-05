import customtkinter as ctk
from gui import theme
from database import (
    user_exists,
    create_user,
    verify_user
)

class LoginPage(ctk.CTkFrame):

    def __init__(self, parent, app):

        super().__init__(
            parent,
            fg_color=theme.BACKGROUND
        )

        self.app = app
        self.status_labels = []
        self.pulse_on = True

        print("LOGIN PAGE CREATED")

        self.build_ui()

        if not user_exists():
            self.after(
                100,
                self.show_setup_screen
            )

        # Make sure the login page is actually visible.
        self.pack(
            fill="both",
            expand=True
        )

        print("LOGIN UI BUILT")

        # Start subtle status animation.
        self.after(
            1000,
            self.animate_status
        )

    # ==========================================================
    # BUILD UI
    # ==========================================================

    def build_ui(self):

        # ======================================================
        # LEFT SIDE
        # ======================================================

        left = ctk.CTkFrame(
            self,
            fg_color=theme.PANEL,
            corner_radius=22
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(30, 12),
            pady=30
        )

        # ------------------------------------------------------
        # BRAND
        # ------------------------------------------------------

        brand = ctk.CTkFrame(
            left,
            fg_color="transparent"
        )

        brand.pack(
            anchor="nw",
            padx=40,
            pady=(35, 0)
        )

        ctk.CTkLabel(
            brand,
            text="🛡",
            font=("Segoe UI Emoji", 34)
        ).pack(
            side="left",
            padx=(0, 12)
        )

        brand_text = ctk.CTkFrame(
            brand,
            fg_color="transparent"
        )

        brand_text.pack(
            side="left"
        )

        ctk.CTkLabel(
            brand_text,
            text="NETGUARD",
            font=("Segoe UI", 26, "bold"),
            text_color=theme.TEXT
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            brand_text,
            text="NETWORK DEFENSE PLATFORM",
            font=("Segoe UI", 10, "bold"),
            text_color=theme.PRIMARY
        ).pack(
            anchor="w"
        )

        # ------------------------------------------------------
        # SECURITY ENGINE CARD
        # ------------------------------------------------------

        engine = ctk.CTkFrame(
            left,
            fg_color=theme.CARD,
            corner_radius=20
        )

        engine.pack(
            fill="x",
            padx=40,
            pady=(45, 25)
        )

        ctk.CTkLabel(
            engine,
            text="🛡",
            font=("Segoe UI Emoji", 58)
        ).pack(
            pady=(20, 5)
        )

        ctk.CTkLabel(
            engine,
            text="SECURITY ENGINE",
            font=("Segoe UI", 18, "bold"),
            text_color=theme.TEXT
        ).pack()

        self.engine_status = ctk.CTkLabel(
            engine,
            text="● SYSTEM READY",
            font=("Segoe UI", 10, "bold"),
            text_color=theme.SUCCESS
        )

        self.engine_status.pack(
            pady=(5, 20)
        )

        # ------------------------------------------------------
        # CAPABILITIES
        # ------------------------------------------------------

        ctk.CTkLabel(
            left,
            text="PROTECTION CAPABILITIES",
            font=("Segoe UI", 11, "bold"),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=40,
            pady=(5, 10)
        )

        self.create_capability(
            left,
            "NETWORK MONITORING",
            "Real-time device discovery and tracking"
        )

        self.create_capability(
            left,
            "ROGUE DEVICE DETECTION",
            "Identify unauthorized network devices"
        )

        self.create_capability(
            left,
            "ARP SPOOFING DEFENSE",
            "Detect suspicious ARP mapping changes"
        )

       
        ctk.CTkLabel(
            left,
            text="NETGUARD SECURITY SYSTEM • v2.0",
            font=("Segoe UI", 9),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            side="bottom",
            pady=15
        )

        # ======================================================
        # RIGHT SIDE
        # ======================================================

        right = ctk.CTkFrame(
            self,
            fg_color=theme.CARD,
            corner_radius=22,
            width=430
        )

        right.pack(
            side="right",
            fill="y",
            padx=(12, 30),
            pady=30
        )

        right.pack_propagate(False)

        # ------------------------------------------------------
        # TITLE
        # ------------------------------------------------------

        ctk.CTkLabel(
            right,
            text="SECURE ACCESS",
            font=("Segoe UI", 28, "bold"),
            text_color=theme.TEXT
        ).pack(
            pady=(75, 8)
        )

        ctk.CTkLabel(
            right,
            text="Sign in to continue to NetGuard",
            font=("Segoe UI", 13),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            pady=(0, 40)
        )

        # ------------------------------------------------------
        # USERNAME
        # ------------------------------------------------------

        ctk.CTkLabel(
            right,
            text="USERNAME",
            font=("Segoe UI", 10, "bold"),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=55
        )

        self.username = ctk.CTkEntry(
            right,
            width=320,
            height=46,
            placeholder_text="Enter username",
            corner_radius=10
        )

        self.username.pack(
            pady=(7, 18)
        )

        # ------------------------------------------------------
        # PASSWORD
        # ------------------------------------------------------

        ctk.CTkLabel(
            right,
            text="PASSWORD",
            font=("Segoe UI", 10, "bold"),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=55
        )

        password_frame = ctk.CTkFrame(
            right,
            fg_color="transparent"
        )

        password_frame.pack(
            pady=(7, 12)
        )

        self.password = ctk.CTkEntry(
            password_frame,
            width=270,
            height=46,
            placeholder_text="Enter password",
            show="*",
            corner_radius=10
        )

        self.password.pack(
            side="left"
        )

        self.show_password = ctk.CTkButton(
            password_frame,
            text="◉",
            width=45,
            height=46,
            corner_radius=10,
            fg_color=theme.PANEL,
            hover_color=theme.PRIMARY,
            command=self.toggle_password
        )

        self.show_password.pack(
            side="left",
            padx=(5, 0)
        )

        # ------------------------------------------------------
        # REMEMBER
        # ------------------------------------------------------

        self.remember = ctk.CTkCheckBox(
            right,
            text="Remember Me",
            font=("Segoe UI", 11)
        )

        self.remember.pack(
            anchor="w",
            padx=55,
            pady=7
        )

        # ------------------------------------------------------
        # MESSAGE
        # ------------------------------------------------------

        self.message = ctk.CTkLabel(
            right,
            text="",
            font=("Segoe UI", 11)
        )

        self.message.pack(
            pady=(5, 0)
        )

        # ------------------------------------------------------
        # LOGIN BUTTON
        # ------------------------------------------------------

        self.login_button = ctk.CTkButton(
            right,
            text="SECURE LOGIN  →",
            width=320,
            height=48,
            corner_radius=10,
            font=("Segoe UI", 14, "bold"),
            fg_color=theme.PRIMARY,
            command=self.login
        )

        self.login_button.pack(
            pady=18
        )

        # ------------------------------------------------------
        # FOOTER
        # ------------------------------------------------------

        ctk.CTkLabel(
            right,
            text="● Protected by NetGuard Security Engine",
            font=("Segoe UI", 10),
            text_color=theme.SUCCESS
        ).pack(
            pady=(12, 5)
        )

        ctk.CTkLabel(
            right,
            text="Authorized access only",
            font=("Segoe UI", 9),
            text_color=theme.TEXT_SECONDARY
        ).pack()

        # Enter key support.

        self.password.bind(
            "<Return>",
            lambda event: self.login()
        )

        self.username.bind(
            "<Return>",
            lambda event: self.login()
        )

    # ==========================================================
    # CAPABILITY
    # ==========================================================

    def create_capability(
        self,
        parent,
        title,
        description
    ):

        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        frame.pack(
            fill="x",
            padx=40,
            pady=5
        )

        ctk.CTkLabel(
            frame,
            text="●",
            font=("Segoe UI", 12, "bold"),
            text_color=theme.SUCCESS,
            width=18
        ).pack(
            side="left"
        )

        text_frame = ctk.CTkFrame(
            frame,
            fg_color="transparent"
        )

        text_frame.pack(
            side="left",
            padx=8
        )

        ctk.CTkLabel(
            text_frame,
            text=title,
            font=("Segoe UI", 10, "bold"),
            text_color=theme.TEXT
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            text_frame,
            text=description,
            font=("Segoe UI", 9),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            anchor="w"
        )

    # ==========================================================
    # STATUS
    # ==========================================================

    def create_status(
        self,
        parent,
        name
    ):

        row = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            padx=16,
            pady=3
        )

        ctk.CTkLabel(
            row,
            text=name,
            font=("Segoe UI", 10),
            text_color=theme.TEXT
        ).pack(
            side="left"
        )

        label = ctk.CTkLabel(
            row,
            text="● READY",
            font=("Segoe UI", 10, "bold"),
            text_color=theme.SUCCESS
        )

        label.pack(
            side="right"
        )

        self.status_labels.append(label)

    # ==========================================================
    # STATUS ANIMATION
    # ==========================================================

    def animate_status(self):

        if not self.winfo_exists():
            return

        self.pulse_on = not self.pulse_on

        color = (
            theme.SUCCESS
            if self.pulse_on
            else theme.TEXT_SECONDARY
        )

        for label in self.status_labels:

            if label.winfo_exists():

                label.configure(
                    text_color=color
                )

        if self.engine_status.winfo_exists():

            self.engine_status.configure(
                text_color=color
            )

        self.after(
            1200,
            self.animate_status
        )

    # ==========================================================
    # PASSWORD
    # ==========================================================

    def toggle_password(self):

        if self.password.cget("show") == "*":

            self.password.configure(
                show=""
            )

        else:

            self.password.configure(
                show="*"
            )


    def show_setup_screen(self):

        for widget in self.winfo_children():
            widget.destroy()

    # =====================================================
    # MAIN SETUP CARD
    # =====================================================

        self.setup_frame = ctk.CTkFrame(
            self,
            fg_color=theme.CARD,
            corner_radius=24,
            width=560,
            height=650
        )

        self.setup_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        self.setup_frame.pack_propagate(False)

    # =====================================================
    # BRAND
    # =====================================================

        ctk.CTkLabel(
            self.setup_frame,
            text="🛡",
            font=("Segoe UI Emoji", 52)
        ).pack(
            pady=(28, 2)
        )

        ctk.CTkLabel(
            self.setup_frame,
            text="NETGUARD",
            font=("Segoe UI", 28, "bold"),
            text_color=theme.PRIMARY
        ).pack()

        ctk.CTkLabel(
            self.setup_frame,
            text="INITIAL SECURITY SETUP",
            font=("Segoe UI", 13, "bold"),
            text_color=theme.TEXT
        ).pack(
            pady=(2, 4)
        )

        ctk.CTkLabel(
            self.setup_frame,
            text="Create the local administrator account",
            font=("Segoe UI", 11),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            pady=(0, 12)
        )

    # =====================================================
    # LOCAL SECURITY BADGE
    # =====================================================

        badge = ctk.CTkFrame(
            self.setup_frame,
            fg_color=theme.PANEL,
            corner_radius=10
        )

        badge.pack(
            padx=80,
            pady=(0, 18),
            fill="x"
        )

        ctk.CTkLabel(
            badge,
            text="●  LOCAL / OFFLINE AUTHENTICATION",
            font=("Segoe UI", 10, "bold"),
            text_color=theme.SUCCESS
        ).pack(
            pady=8
        )

    # =====================================================
    # USERNAME
    # =====================================================

        ctk.CTkLabel(
            self.setup_frame,
            text="USERNAME",
            font=("Segoe UI", 10, "bold"),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=80
        )

        self.setup_username = ctk.CTkEntry(
            self.setup_frame,
            width=400,
            height=42,
            placeholder_text="Choose administrator username",
            corner_radius=10
        )

        self.setup_username.pack(
            pady=(5, 12)
        )

    # =====================================================
    # PASSWORD CONTAINER
    # =====================================================

        ctk.CTkLabel(
            self.setup_frame,
            text="PASSWORD",
            font=("Segoe UI", 10, "bold"),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=80
        )

        password_frame = ctk.CTkFrame(
            self.setup_frame,
            fg_color="transparent"
        )

        password_frame.pack(
            padx=80,
            fill="x"
        )

        self.setup_password = ctk.CTkEntry(
            password_frame,
            height=42,
            placeholder_text="Create password",
            show="*",
            corner_radius=10
        )

        self.setup_password.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.setup_password_eye = ctk.CTkButton(
            password_frame,
            text="👁",
            width=42,
            height=42,
            corner_radius=10,
            fg_color=theme.PANEL,
            hover_color=theme.BORDER,
            command=self.toggle_setup_password
        )

        self.setup_password_eye.pack(
            side="left",
            padx=(6, 0)
        )

    # =====================================================
    # PASSWORD STRENGTH
    # =====================================================

        self.password_strength = ctk.CTkLabel(
            self.setup_frame,
            text="Password strength: —",
            font=("Segoe UI", 10),
            text_color=theme.TEXT_SECONDARY
        )

        self.password_strength.pack(
            anchor="w",
            padx=80,
            pady=(4, 10)
        )

        self.setup_password.bind(
            "<KeyRelease>",
            self.update_password_strength
        )

    # =====================================================
    # CONFIRM PASSWORD
    # =====================================================

        ctk.CTkLabel(
            self.setup_frame,
            text="CONFIRM PASSWORD",
            font=("Segoe UI", 10, "bold"),
            text_color=theme.TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=80
        )

        confirm_frame = ctk.CTkFrame(
            self.setup_frame,
            fg_color="transparent"
        )

        confirm_frame.pack(
            padx=80,
            fill="x"
        )

        self.setup_confirm = ctk.CTkEntry(
            confirm_frame,
            height=42,
            placeholder_text="Confirm password",
            show="*",
            corner_radius=10
        )

        self.setup_confirm.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.setup_confirm_eye = ctk.CTkButton(
            confirm_frame,
            text="👁",
            width=42,
            height=42,
            corner_radius=10,
            fg_color=theme.PANEL,
            hover_color=theme.BORDER,
            command=self.toggle_setup_confirm
        )

        self.setup_confirm_eye.pack(
            side="left",
            padx=(6, 0)
        )

    # =====================================================
    # MESSAGE
    # =====================================================

        self.setup_message = ctk.CTkLabel(
            self.setup_frame,
            text="",
            font=("Segoe UI", 10)
        )

        self.setup_message.pack(
            pady=(8, 4)
        )

    # =====================================================
    # CREATE BUTTON
    # =====================================================

        self.setup_button = ctk.CTkButton(
            self.setup_frame,
            text="CREATE SECURE ACCOUNT  →",
            width=400,
            height=46,
            corner_radius=10,
            font=("Segoe UI", 12, "bold"),
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_HOVER,
            command=self.create_first_account
        )

        self.setup_button.pack(
            pady=(5, 8)
       )
 
        ctk.CTkLabel(
            self.setup_frame,
            text="Your password is stored locally as a secure hash.",
            font=("Segoe UI", 9),
            text_color=theme.TEXT_SECONDARY
        ).pack()

        # Enter key
        self.setup_confirm.bind(
            "<Return>",
            lambda event: self.create_first_account()
        )

    def create_first_account(self):

        username = self.setup_username.get().strip()
        password = self.setup_password.get()
        confirm = self.setup_confirm.get()

        if not username or not password or not confirm:

            self.setup_message.configure(
                text="✕ All fields are required",
                text_color=theme.DANGER
            )

            return

        if len(username) < 3:

            self.setup_message.configure(
                text="✕ Username must be at least 3 characters",
                text_color=theme.DANGER
            )

            return

        if len(password) < 8:

            self.setup_message.configure(
                text="✕ Password must be at least 8 characters",
                text_color=theme.DANGER
            )

            return

        if password != confirm:

            self.setup_message.configure(
                text="✕ Passwords do not match",
                text_color=theme.DANGER
            )

            return

        created = create_user(
            username,
            password
        )

        if not created:

            self.setup_message.configure(
                text="✕ Unable to create account",
                text_color=theme.DANGER
            )

            return

        self.setup_message.configure(
            text="✓ Account created successfully",
            text_color=theme.SUCCESS
        )

        self.after(
            1000,
            self.restore_login_screen
        )

    def toggle_setup_password(self):

        if self.setup_password.cget("show") == "*":
            self.setup_password.configure(show="")
            self.setup_password_eye.configure(text="🙈")
        else:
            self.setup_password.configure(show="*")
            self.setup_password_eye.configure(text="👁")

    def toggle_setup_confirm(self):

        if self.setup_confirm.cget("show") == "*":
            self.setup_confirm.configure(show="")
            self.setup_confirm_eye.configure(text="🙈")
        else:
            self.setup_confirm.configure(show="*")
            self.setup_confirm_eye.configure(text="👁")

    def update_password_strength(self, event=None):

        password = self.setup_password.get()

        if not password:

            self.password_strength.configure(
                text="Password strength: —",
                text_color=theme.TEXT_SECONDARY
            )

            return

        score = 0

        if len(password) >= 8:
            score += 1

        if len(password) >= 12:
            score += 1

        if any(c.isupper() for c in password):
            score += 1

        if any(c.isdigit() for c in password):
            score += 1

        if any(not c.isalnum() for c in password):
            score += 1

        if score <= 2:

            text = "Password strength: WEAK"
            color = theme.DANGER

        elif score <= 3:

            text = "Password strength: MEDIUM"
            color = "#F59E0B"

        else:

            text = "Password strength: STRONG"
            color = theme.SUCCESS

        self.password_strength.configure(
            text=text,
            text_color=color
        )

    
    def restore_login_screen(self):

        for widget in self.winfo_children():
            widget.destroy()

        self.status_labels = []
        self.pulse_on = True

        self.build_ui()

    # ==========================================================
    # LOGIN
    # ==========================================================

    def login(self):

        username = self.username.get().strip()
        password = self.password.get()

    # ------------------------------------------------------
    # EMPTY FIELDS
    # ------------------------------------------------------

        if not username or not password:

            self.message.configure(
                text="✕ Enter username and password",
                text_color=theme.DANGER
            )

            return

    # ------------------------------------------------------
    # AUTHENTICATE
    # ------------------------------------------------------

        if not verify_user(username, password):

            self.message.configure(
                text="✕ Invalid username or password",
                text_color=theme.DANGER
            )

            self.login_button.configure(
                text="ACCESS DENIED",
                fg_color=theme.DANGER
            )

            self.after(
                1500,
                self.reset_login
            )

            return

    # ------------------------------------------------------
    # AUTHENTICATING
    # ------------------------------------------------------

        self.username.configure(
            state="disabled"
        )

        self.password.configure(
            state="disabled"
        )

        self.remember.configure(
            state="disabled"
        )

        self.show_password.configure(
            state="disabled"
        )

        self.login_button.configure(
            text="AUTHENTICATING...",
            state="disabled",
            fg_color=theme.PRIMARY
        )

        self.message.configure(
            text="Verifying secure credentials...",
            text_color=theme.PRIMARY
        )

        self.engine_status.configure(
            text="● VERIFYING ACCESS..."
        )

        self.after(
            800,
            self.login_success
        )

    # ==========================================================
    # SUCCESS
    # ==========================================================

    def login_success(self):

        self.app.current_username = self.username.get().strip()

        self.message.configure(
            text="✓ ACCESS GRANTED",
            text_color=theme.SUCCESS
        )

        self.login_button.configure(
            text="✓ SECURE ACCESS GRANTED",
            fg_color=theme.SUCCESS
        )

        self.engine_status.configure(
            text="● ACCESS VERIFIED",
            text_color=theme.SUCCESS
        )

        self.after(
            700,
            self.open_dashboard
        )

    # ==========================================================
    # OPEN DASHBOARD
    # ==========================================================

    def open_dashboard(self):

        # Let the main application handle page switching.

        self.pack_forget()

        self.app.show_dashboard()

    # ==========================================================
    # RESET
    # ==========================================================

    def reset_login(self):

        self.login_button.configure(
            text="SECURE LOGIN  →",
            fg_color=theme.PRIMARY,
            state="normal"
        )

        self.username.configure(
            state="normal"
        )

        self.password.configure(
            state="normal"
        )

        self.remember.configure(
            state="normal"
        )

        self.show_password.configure(
            state="normal"
        )

        self.message.configure(
            text=""
        )

        self.engine_status.configure(
            text="● SYSTEM READY"
        )