from datetime import datetime
from database import create_database, save_device,mark_all_devices_offline,get_device
from scapy.all import ARP, Ether, srp
from vendor_database import load_vendor_database, get_vendor
from device_identifier import identify_device
from device_names import get_device_name
vendor_database = load_vendor_database()
from services.network_detector import NetworkDetector
from database import is_trusted


def scan_network():

    network = NetworkDetector.get_network_info()

    if network is None:
        print("❌ IPv4 network not available.")
        return []

    target_ip = network["subnet"]

    print("Scanning:", target_ip)

    arp = ARP(pdst=target_ip)

    ether = Ether(dst="ff:ff:ff:ff:ff:ff")

    packet = ether / arp

    result = srp(
        packet,
        timeout=5,
        verbose=0
    )[0]

    return result

def process_devices(result):
    devices = []
    for _, received in result:

        vendor = get_vendor(received.hwsrc, vendor_database)
        device_type = identify_device(vendor)
        device_name = get_device_name(received.hwsrc)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        is_new = save_device(
            received.hwsrc.upper(),
            received.psrc,
            device_name,
            vendor,
            device_type,
            current_time,
            current_time,
            "Active"
        )
        device = get_device(received.hwsrc.upper())
        device["is_new"] = is_new
        device["is_trusted"] = is_trusted(received.hwsrc.upper())
        print(device["device_name"], "Trusted:", device["is_trusted"])

        devices.append(device)

        print(f"{'IP Address':<12}: {received.psrc}")
        print(f"{'MAC Address':<12}: {received.hwsrc.upper()}")
        print(f"{'Vendor':<12}: {vendor}")
        print(f"{'Device Type':<12}: {device_type}")
        print(f"{'Device Name':<12}: {device_name}")
        print("-" * 45)

        if is_new:
            print("\n🚨 NEW DEVICE DETECTED! 🚨")
            print(f"Device Name : {device_name}")
            print(f"IP Address  : {received.psrc}")
            print(f"MAC Address : {received.hwsrc.upper()}")
            print(f"Vendor      : {vendor}")
            print(f"Device Type : {device_type}")
            print("-" * 45)
    return devices

def main():
    create_database()
    mark_all_devices_offline()

    result = scan_network()

    devices = process_devices(result)


if __name__ == "__main__":
    main()
  


   
   
    