trusted_devices = set()

def load_trusted_devices():
    return trusted_devices

def add_trusted_device(mac):
    trusted_devices.add(mac.upper())

def is_trusted(mac):
    return mac.upper() in trusted_devices