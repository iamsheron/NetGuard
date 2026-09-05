from scapy.all import ARP, Ether, srp
from services.alert_manager import AlertManager
from services.notification_manager import NotificationManager
from core import shared_state

alert_manager = AlertManager()
notification_manager = NotificationManager()


class ARPSpoofDetector:

    def __init__(self):
        self.arp_table = {}

    def build_baseline(self, network):

        print("📡 Building ARP baseline...")

        request = ARP(pdst=network)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")

        packet = broadcast / request

        answered = srp(
            packet,
            timeout=3,
            verbose=False
        )[0]

        for _, received in answered:

            ip = received.psrc
            mac = received.hwsrc.upper()

            self.arp_table[ip] = mac

            print(
                f"[ARP BASELINE] "
                f"{ip} -> {mac}"
            )

        print()
        print("✅ ARP baseline scan finished.")
        print("Known devices:")

        for ip, mac in self.arp_table.items():
            print(f"   {ip} -> {mac}")

    def check_mapping(self, ip, mac):

        mac = mac.upper()

        if ip not in self.arp_table:

            self.arp_table[ip] = mac

            print(
                f"[ARP NEW] "
                f"{ip} -> {mac}"
            )

            return None

        expected_mac = self.arp_table[ip]

        if expected_mac != mac:

            alert = {
                "type": "ARP_SPOOFING",
                "ip": ip,
                "expected_mac": expected_mac,
                "observed_mac": mac
            }
            security_alert = alert_manager.raise_alert(
                level="CRITICAL",
                title="🚨 ARP Spoofing Detected",
                message=(
                    f"IP {ip} changed from "
                    f"{expected_mac} to {mac}."
                ),
                device={
                    "ip": ip,
                    "expected_mac": expected_mac,
                    "observed_mac": mac
                }
            )

            
            notification_manager.notify(security_alert)

            print()
            print("=" * 50)
            print("🚨 POSSIBLE ARP SPOOFING DETECTED")
            print("=" * 50)
            print(f"IP Address  : {ip}")
            print(f"Expected MAC: {expected_mac}")
            print(f"Observed MAC : {mac}")
            print("=" * 50)

            return alert

        return None
    def monitor(self):

        print("🛡 Live ARP monitoring started...")
      
        from scapy.all import sniff, ARP

        def handle_packet(packet):

            if not packet.haslayer(ARP):
                return

            arp = packet[ARP]

            if arp.op != 2:
                return

            result = self.check_mapping(
                arp.psrc,
                arp.hwsrc
            )

            if result:
                print("⚠ Security event detected!")

        sniff(
            filter="arp",
            prn=handle_packet,
            store=False
        )