\# NETGUARD



\*\*NETGUARD\*\* is a Windows desktop network security monitoring application designed to help users discover devices on their local network, analyze network activity, identify potential risks, and receive security notifications.



\## Features



\* 🔍 Network device discovery and scanning

\* 🖥️ Device identification and device details

\* 🏷️ Vendor/OUI-based device identification

\* 🛡️ ARP-based network monitoring

\* ⚠️ Risk analysis and rogue-device detection

\* 🔌 Network port scanning

\* 📊 Security dashboard and scan activity visualization

\* 📄 Security report generation

\* 📱 Telegram security notifications

\* ☁️ Automatic Cloudflare Quick Tunnel integration for the Telegram server

\* ⚙️ Configurable application settings

\* 🧪 Automated tests for important components



\## Architecture



NETGUARD is organized into several main components:



```text

NETGUARD/

│

├── launcher.py

├── main.py

├── database.py

├── arp\_detector.py

├── device\_identifier.py

├── device\_names.py

├── pdf\_report.py

├── stage1\_scan.py

├── telegram\_notifier.py

├── vendor\_database.py

├── oui.csv

│

├── core/

│   ├── shared\_state.py

│   └── trusted\_devices.py

│

├── gui/

│   ├── app.py

│   ├── dashboard.py

│   ├── device\_details\_panel.py

│   ├── device\_table.py

│   ├── general\_tab.py

│   ├── login.py

│   ├── modern\_dialog.py

│   ├── network\_status.py

│   ├── ports\_tab.py

│   ├── port\_scanner.py

│   ├── scan\_activity\_graph.py

│   ├── security\_center.py

│   ├── security\_tab.py

│   ├── settings\_page.py

│   ├── stat\_card.py

│   └── theme.py

│

├── services/

│   ├── alert\_manager.py

│   ├── network\_detector.py

│   ├── notification\_manager.py

│   ├── os\_detector.py

│   └── risk\_analyzer.py

│

├── telegram\_server/

│   └── server.py

│

└── tests/

&#x20;   ├── test\_arp\_detector.py

&#x20;   ├── test\_os.py

&#x20;   ├── test\_pdf\_report.py

&#x20;   └── test\_telegram.py

```



\## Requirements



NETGUARD uses Python and the following third-party packages:



```text

customtkinter

scapy

python-dotenv

requests

reportlab

Flask

python-nmap

```



The project also requires \*\*Nmap\*\* to be installed on Windows for the Nmap-based functionality.



\## Installation



\### 1. Clone the repository



```powershell

git clone <YOUR-GITHUB-REPOSITORY-URL>

cd NetGuard

```



\### 2. Create a virtual environment



```powershell

python -m venv .venv

```



Activate it:



```powershell

.venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```powershell

pip install -r requirements.txt

```



\### 4. Configure environment variables



Create a local `.env` file:



```text

NETGUARD\_TELEGRAM\_TOKEN=YOUR\_TELEGRAM\_BOT\_TOKEN

```



\*\*Never commit `.env` to GitHub.\*\*



The `.env` file is intentionally excluded by `.gitignore`.



\## Running NETGUARD



NETGUARD is launched through the automatic launcher:



```powershell

python launcher.py

```



The launcher starts the required background components and then starts the NETGUARD desktop application.



The launcher is responsible for coordinating the Telegram server and Cloudflare Quick Tunnel before starting the GUI.



\## Telegram Notifications



NETGUARD can send security alerts through Telegram.



The Telegram integration uses:



\* A Telegram bot

\* The locally running NETGUARD Telegram server

\* A dynamically generated Cloudflare Quick Tunnel

\* A webhook connection between Telegram and the local server



The Cloudflare tunnel URL is generated dynamically when NETGUARD starts. It is therefore \*\*not permanently hardcoded into the application\*\*.



The current tunnel information is handled at runtime.



\## Security



Sensitive configuration should remain local.



The following types of files are excluded from version control:



```text

.env

\*.db

\*.sqlite

\*.sqlite3

\*.log

generated reports

runtime tunnel information

installation information

Python cache files

IDE configuration

```



Never publish:



\* Telegram bot tokens

\* API keys

\* passwords

\* private credentials

\* local databases containing sensitive information

\* personal installation identifiers



\## Testing



The project contains tests covering important components including:



\* ARP detection

\* Operating-system detection

\* PDF report generation

\* Telegram functionality



Run the test suite with:



```powershell

python -m unittest discover

```



Individual tests can also be executed directly, for example:



```powershell

python test\_arp\_detector.py

```



\## Reports



NETGUARD can generate security reports containing information collected during network analysis.



Generated reports are treated as runtime artifacts and are not intended to be committed to the source repository.



\## Project Status



NETGUARD is currently in a functional development stage with the primary desktop security-monitoring features implemented.



The project is being prepared for public source-code publication and continued development.



\## Disclaimer



NETGUARD is intended for network monitoring and security analysis on networks and devices that you own or have permission to inspect.



Only use network scanning, device discovery, port scanning, and monitoring features in authorized environments.



\## License



This project will be distributed under the license specified in the repository.



\---



\*\*NETGUARD — Local Network Security Monitoring\*\*



