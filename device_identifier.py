DEVICE_RULES = {
    "Liteon": "Laptop",
    "Intel": "Computer",
    "Apple": "Apple Device",
    "Samsung": "Phone / TV",
    "Cisco": "Network Device",
    "TP-Link": "Router",
    "D-Link": "Router",
    "Nokia": "Network Equipment",
    "PPC":"Router",
}


def identify_device(vendor):

    for keyword, device in DEVICE_RULES.items():

        if keyword in vendor:
            return device

    return "Unknown Device"