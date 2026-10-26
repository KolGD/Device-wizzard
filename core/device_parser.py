import re

from core.device_info import get_device_info


# The PCI class and revision must not be mistaken for the vendor:device ID.
PCI_DEVICE_PATTERN = re.compile(
    r"^(?P<address>(?:[0-9a-f]{4}:)?[0-9a-f]{2}:[0-9a-f]{2}\.[0-7])"
    r"\s+[^:]+:\s*(?P<name>.*?)\s*"
    r"\[(?P<id>[0-9a-f]{4}:[0-9a-f]{4})\]",
    re.IGNORECASE,
)

USB_DEVICE_PATTERN = re.compile(
    r"^Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+):\s+"
    r"ID\s+(?P<id>[0-9a-f]{4}:[0-9a-f]{4})(?:\s+(?P<name>.*))?$",
    re.IGNORECASE,
)


def parse_pci_devices(raw_output):
    devices = []
    current_device = None

    for line in raw_output.splitlines():
        if not line.strip():
            continue

        if not line[0].isspace():
            # Reset here so a malformed header cannot inherit the previous device.
            current_device = None
            match = PCI_DEVICE_PATTERN.match(line)
            if match is None:
                continue

            current_device = {
                "address": match["address"].lower(),
                "name": match["name"].strip() or "Unknown",
                "id": match["id"].lower(),
                "driver": None,
            }
            devices.append(current_device)

        elif current_device is not None:
            details = line.strip()
            if details.startswith("Kernel driver in use:"):
                current_device["driver"] = details.split(":", 1)[1].strip() or None

    return devices


def parse_usb_devices(raw_output):
    devices = []

    for line in raw_output.splitlines():
        match = USB_DEVICE_PATTERN.fullmatch(line.strip())
        if match is None:
            continue

        devices.append({
            "bus": match["bus"],
            "device": match["device"],
            "id": match["id"].lower(),
            "name": (match["name"] or "").strip() or "Unknown",
        })

    return devices


def enrich_devices(devices, device_type):
    for device in devices:
        info = get_device_info(device["id"], device_type)
        device["manufacturer"] = info["manufacturer"]
        device["type"] = info["type"]

        # A failed database lookup must not erase the name from lspci/lsusb.
        if info["name"] and info["name"] != "Unknown":
            device["name"] = info["name"]
        elif not device.get("name"):
            device["name"] = "Unknown"

    return devices
