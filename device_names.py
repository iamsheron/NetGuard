DEVICE_NAMES = {
    "70:08:94:6D:8D:85": "Sheron's Laptop",
    "64:FB:92:38:5B:A1": "Home Router",
}


def get_device_name(mac):
    return DEVICE_NAMES.get(mac.upper(), "Unknown Device")