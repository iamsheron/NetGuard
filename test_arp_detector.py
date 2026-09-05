from arp_detector import ARPSpoofDetector


detector = ARPSpoofDetector()

# Simulated trusted baseline
detector.arp_table = {
    "192.168.1.1": "64:FB:92:38:5B:A1"
}

print("========================================")
print("NETGUARD ARP SPOOFING OFFICIAL TEST")
print("========================================")

print("\n1. Testing normal ARP mapping...")

result = detector.check_mapping(
    "192.168.1.1",
    "64:FB:92:38:5B:A1"
)

if result is None:
    print("✅ Normal mapping correctly ignored.")
else:
    print("❌ FAIL: Normal mapping generated an alert.")


print("\n2. Testing suspicious ARP mapping...")

result = detector.check_mapping(
    "192.168.1.1",
    "AA:BB:CC:DD:EE:FF"
)

if result and result.get("type") == "ARP_SPOOFING":

    print("✅ ARP spoofing correctly detected!")

    print("\nDetection details:")
    print(f"IP Address  : {result['ip']}")
    print(f"Expected MAC: {result['expected_mac']}")
    print(f"Observed MAC : {result['observed_mac']}")

else:

    print("❌ FAIL: ARP spoofing was not detected.")


print("\n========================================")
print("TEST COMPLETE")
print("========================================")