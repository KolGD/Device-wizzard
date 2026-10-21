def get_vendor_id(device_id):
    return device_id.split(":")[0]


def find_vendor_name(device_id, database_path):
    vendor_id = get_vendor_id(device_id)

    with open(database_path, "r") as file:
        for line in file:
            if line.startswith(vendor_id + " "):
                return line[6:].strip()

    return "Unknown"


def get_vendor_name(device_id):
    return find_vendor_name(device_id, "/usr/share/hwdata/pci.ids")


def get_usb_vendor_name(device_id):
    return find_vendor_name(device_id, "/usr/share/hwdata/usb.ids")


def get_pci_device_name(device_id):
    vendor_id, device_id = device_id.split(":")
    database_path = "/usr/share/hwdata/pci.ids"
    inside_vendor = False

    with open(database_path, "r") as file:
        for line in file:
            if line.startswith(vendor_id + " "):
                inside_vendor = True
                continue

            if inside_vendor:
                if line.startswith("#"):
                    continue

                if line and not line[0].isspace():
                    break

                parts = line.strip().split(None, 1)

                if len(parts) == 2 and parts[0] == device_id:
                    return parts[1]

    return "Unknown"


def get_usb_device_name(device_id):
    vendor_id, device_id = device_id.split(":")
    database_path = "/usr/share/hwdata/usb.ids"
    inside_vendor = False

    with open(database_path, "r") as file:
        for line in file:
            if line.startswith(vendor_id + " "):
                inside_vendor = True
                continue

            if inside_vendor and line and not line[0].isspace():
                break

            if inside_vendor:
                parts = line.strip().split(None, 1)

                if len(parts) == 2 and parts[0] == device_id:
                    return parts[1].strip()

    return "Unknown"


def get_device_info(device_id, device_type):
    if device_type == "PCI":
        manufacturer = get_vendor_name(device_id)
        name = get_pci_device_name(device_id)

    elif device_type == "USB":
        manufacturer = get_usb_vendor_name(device_id)
        name = get_usb_device_name(device_id)

    else:
        manufacturer = "Unknown"
        name = "Unknown"

    return {
        "id": device_id,
        "manufacturer": manufacturer,
        "name": name,
        "type": device_type
    }