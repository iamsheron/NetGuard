# NETGUARD

Windows desktop network security monitoring application built with Python.

NETGUARD is designed to help users discover devices on a local network, inspect device information, detect suspicious ARP activity, scan ports, assess security risks, and receive security notifications through Telegram.

## Features

* Network device discovery
* Device identification and vendor lookup
* MAC address and OUI lookup
* ARP spoofing detection
* Port scanning
* Operating-system detection
* Device risk analysis
* Trusted-device management
* Security alerts
* SQLite-based local data storage
* PDF security reports
* Telegram security notifications

## Architecture

NETGUARD is a Windows desktop application with a Python GUI and several supporting services.

```text
NETGUARD
│
├── launcher.py
│   ├── Starts the local Telegram Flask server
│   ├── Starts the Cloudflare Quick Tunnel
│   ├── Detects the public tunnel URL
│   ├── Configures the Telegram webhook
│   └── Starts the main application
│
├── main.py
│   └── Starts the NETGUARD desktop application
│
├── gui/
│   ├── app.py
│   ├── dashboard.py
│   ├── device_details_panel.py
│   ├── device_table.py
│   ├── general_tab.py
│   ├── login.py
│   ├── modern_dialog.py
│   ├── network_status.py
│   ├── port_scanner.py
│   ├── ports_tab.py
│   ├── scan_activity_graph.py
│   ├── security_center.py
│   ├── security_tab.py
│   ├── settings_page.py
│   ├── stat_card.py
│   └── theme.py
│
├── services/
│   ├── alert_manager.py
│   ├── network_detector.py
│   ├── notification_manager.py
│   ├── os_detector.py
│   └── risk_analyzer.py
│
├── telegram_server/
│   └── server.py
│
├── core/
│   ├── shared_state.py
│   └── trusted_devices.py
│
├── database.py
├── arp_detector.py
├── device_identifier.py
├── device_names.py
├── pdf_report.py
├── stage1_scan.py
├── telegram_notifier.py
├── vendor_database.py
├── oui.csv
│
└── test_*.py
```

### Runtime flow

```text
User
 │
 ▼
launcher.py
 │
 ├── Flask Telegram Server
 │        │
 │        ▼
 │   Local webhook endpoint
 │
 ├── Cloudflare Quick Tunnel
 │        │
 │        ▼
 │   Public HTTPS webhook
 │
 └── main.py
          │
          ▼
       NETGUARD GUI
          │
          ├── Network Discovery
          ├── ARP Monitoring
          ├── Port Scanning
          ├── OS Detection
          ├── Risk Analysis
          ├── Database
          └── Telegram Notifications
```

## Technology Stack

### Programming Language

* Python

### Desktop GUI

* CustomTkinter
* Tkinter

### Network Security

* Scapy
* ARP monitoring
* Network discovery
* Port scanning
* Nmap

### Database

* SQLite

### Reporting

* ReportLab

### Notifications

* Telegram Bot API
* Requests

### Webhook Server

* Flask

### Environment Configuration

* python-dotenv

### Public Tunnel

* Cloudflare Quick Tunnel

## Requirements

NETGUARD is currently designed for Windows.

You should have:

* Windows 10 or Windows 11
* Python 3.x
* Nmap
* Git
* Internet access for Telegram and Cloudflare tunnel functionality

Python dependencies are listed in:

```text
requirements.txt
```

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/srnnkl904-netizen/NetGuard.git
cd NetGuard
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, you may need to adjust the execution policy for your user account.

### 3. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 4. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 5. Install Nmap

NETGUARD uses Nmap for operating-system detection.

Nmap must be installed separately from the Python package.

After installation, verify that Nmap is available:

```powershell
nmap --version
```

The Python package `python-nmap` is only a Python interface to Nmap; it does not replace the Nmap executable.

## Configuration

NETGUARD uses environment variables for sensitive configuration.

Create a local `.env` file in the project directory:

```text
NETGUARD_TELEGRAM_TOKEN=YOUR_BOT_TOKEN
```

Replace `YOUR_BOT_TOKEN` with the token provided by Telegram's BotFather.

### Important

Never commit `.env` to Git.

The repository's `.gitignore` is configured to exclude the local environment file and other runtime-generated data.

Do not publish your Telegram bot token, passwords, database files, or other private configuration files.

## Running NETGUARD

The recommended way to start the application is:

```powershell
python launcher.py
```

The launcher coordinates the supporting services before starting the desktop interface.

The general startup sequence is:

```text
launcher.py
    ↓
Load environment configuration
    ↓
Start Flask Telegram server
    ↓
Start Cloudflare Quick Tunnel
    ↓
Detect public tunnel URL
    ↓
Configure Telegram webhook
    ↓
Start NETGUARD GUI
```

## Telegram Notifications

NETGUARD can send security notifications through Telegram.

The Telegram integration uses the following architecture:

```text
Telegram
    │
    ▼
Telegram Bot API
    │
    ▼
Cloudflare HTTPS Quick Tunnel
    │
    ▼
Local Flask Server
    │
    ▼
NETGUARD
```

The application stores Telegram connection information locally and uses a generated connection code when establishing a connection.

Telegram settings can be managed from the NETGUARD Settings page.

### Quick Tunnel limitation

NETGUARD currently uses a Cloudflare Quick Tunnel for development and testing.

Quick Tunnel URLs are temporary and can change when the tunnel is restarted.

The current Telegram architecture is intended primarily for local development/testing and a single active installation using the configured bot webhook.

A production multi-user deployment would require a different architecture, such as a centralized backend or another webhook-routing design.

## Security

NETGUARD handles security-sensitive information such as:

* Telegram bot configuration
* Local administrator credentials
* Network device information
* Security alerts
* Local database records

The application keeps sensitive configuration outside the source repository where possible.

Administrator passwords are stored locally as password hashes rather than plain text.

Users should still protect their local NETGUARD installation and never share:

* `.env`
* Telegram bot tokens
* Local databases
* Private configuration files
* Generated security reports containing sensitive network information

## Reports

NETGUARD can generate PDF security reports containing information collected during network monitoring and analysis.

Generated reports are runtime artifacts and should not normally be committed to the source repository.

## Testing

The project contains Python test files for important components, including:

* ARP detection
* Operating-system detection
* PDF report generation
* Telegram notification functionality

To run the tests, use:

```powershell
python -m unittest discover
```

Individual test files can also be executed directly, for example:

```powershell
python test_arp_detector.py
```

## Development

A typical development workflow is:

```text
Edit code
   ↓
Run tests
   ↓
Run NETGUARD
   ↓
Verify the feature
   ↓
Check Git status
   ↓
Commit changes
   ↓
Push to GitHub
```

## Project Status

NETGUARD is an actively developed Windows desktop network-security monitoring project.

The current implementation focuses on local network monitoring, security analysis, reporting, and Telegram-based notifications.

Future development may include:

* Improved network visualization
* Additional security detection techniques
* More advanced reporting
* Better deployment and packaging
* Production-ready Telegram architecture
* Additional automated tests
* Improved cross-platform support

## Disclaimer

NETGUARD is intended for defensive security monitoring and authorized network administration.

Only use network discovery, scanning, ARP monitoring, and related security features on networks and systems that you own or are authorized to test.

The authors are not responsible for misuse of the software.

## License

A license has not yet been selected for this project.

If the project is later released under an open-source license, the appropriate license file and terms will be added to the repository.
