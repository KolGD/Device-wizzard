from core.device_info import get_device_info

def parse_pci_devices(raw_output):
    devices = []
    current_device = None

    for line in raw_output.splitlines():
        if line and not line[0].isspace():
            device = {
                "address": line.split()[0],
                "name": line.split(": ", 1)[1],
                "id": None,
                "driver": None
            }

            device_id = device["name"].split("[")[-1].split("]")[0]
            device["name"] = device["name"].rsplit("[", 1)[0].strip()
            device["id"] = device_id

            devices.append(device)
            current_device = device

        elif "Kernel driver in use:" in line and current_device is not None:
            driver = line.split("Kernel driver in use:", 1)[1].strip()
            current_device["driver"] = driver

    return devices

def parse_usb_devices(raw_output):
    devices = []

    for line in raw_output.splitlines():
        parts = line.split(" ", 5)

        device = {
            "bus": parts[1],
            "device": parts[3].rstrip(":"),
            "id": parts[5].split(" ", 1)[0],
            "name": parts[5].split(" ", 1)[1]
        }

        devices.append(device)

    return devices

def enrich_devices(devices, device_type):
    for device in devices:
        info = get_device_info(device["id"], device_type)

        device["manufacturer"] = info["manufacturer"]
        device["name"] = info["name"]

    return devices