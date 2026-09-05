import subprocess
import re
import ipaddress
import subprocess


class NetworkDetector:

    
    @staticmethod
    def get_network_info():

        output = subprocess.check_output(
            "ipconfig /all",
            text=True,
            encoding="utf-8"
        )
       

        sections = output.split("\n\n")

        for section in sections:

            # Ignore VirtualBox
            if "VirtualBox" in section:
                continue

            # Ignore disconnected adapters
            if "Media disconnected" in section:
                continue

            # Look for an IPv4 address
            ip_match = re.search(
                r"IPv4 Address.*?:\s*([\d.]+)",
                section
            )

            if not ip_match:
                continue

            ipv4 = ip_match.group(1)

            print("Detected IPv4:", ipv4)

            # Ignore APIPA
            if ipv4.startswith("169.254"):
                continue

            network = ipaddress.IPv4Network(
                ipv4 + "/24",
                strict=False
            )

            return {
                "ipv4": ipv4,
                "subnet": str(network)
            }

        return None