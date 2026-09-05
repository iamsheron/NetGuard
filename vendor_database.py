import csv
from pathlib import Path

def load_vendor_database():
    vendor_database = {}

    csv_path = Path(__file__).parent / "oui.csv"

    with open(csv_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)

        next(reader)

        for row in reader:
            vendor_database[row[1]] = row[2]

    return vendor_database


def get_vendor(mac, vendor_database):
    oui = "".join(mac.split(":")[:3]).upper()
    return vendor_database.get(oui, "Unknown Vendor")