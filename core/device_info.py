PCI_DATABASE_PATHS = (
    "/usr/share/hwdata/pci.ids",
    "/usr/share/misc/pci.ids",
    "/var/lib/pciutils/pci.ids",
)

USB_DATABASE_PATHS = (
    "/usr/share/hwdata/usb.ids",
    "/usr/share/misc/usb.ids",
    "/var/lib/usbutils/usb.ids",
)


def _split_device_id(device_id):
    """Return normalized vendor/product IDs, or empty strings for invalid IDs."""
    if not isinstance(device_id, str):
        return "", ""

    parts = [part.strip().lower() for part in device_id.split(":")]
    if len(parts) != 2:
        return "", ""

    for part in parts:
        if len(part) != 4 or any(char not in "0123456789abcdef" for char in part):
            return "", ""

    return parts[0], parts[1]


def get_vendor_id(device_id):
    vendor_id, _ = _split_device_id(device_id)
    return vendor_id


def _read_database(database_paths):
    """Use the first readable local database; missing databases are optional."""
    for database_path in database_paths:
        try:
            with open(database_path, "r", encoding="utf-8", errors="replace") as file:
                return file.readlines()
        except OSError:
            continue

    return []


def _find_names(device_id, database_paths):
    vendor_id, product_id = _split_device_id(device_id)
    if not vendor_id:
        return "Unknown", "Unknown"

    vendor_name = "Unknown"
    inside_vendor = False

    for line in _read_database(database_paths):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        parts = stripped.split(None, 1)

        # Manufacturer rows have no indentation; the next row ends this block.
        if not line[0].isspace():
            if inside_vendor:
                break
            if len(parts) == 2 and parts[0].lower() == vendor_id:
                vendor_name = parts[1].strip()
                inside_vendor = True
            continue

        # Two tabs mark PCI subsystems or USB interfaces, not device names.
        if inside_vendor and line.startswith("\t") and not line.startswith("\t\t"):
            if len(parts) == 2 and parts[0].lower() == product_id:
                return vendor_name, parts[1].strip()

    return vendor_name, "Unknown"


def find_vendor_name(device_id, database_path):
    manufacturer, _ = _find_names(device_id, (database_path,))
    return manufacturer


def get_vendor_name(device_id):
    manufacturer, _ = _find_names(device_id, PCI_DATABASE_PATHS)
    return manufacturer


def get_usb_vendor_name(device_id):
    manufacturer, _ = _find_names(device_id, USB_DATABASE_PATHS)
    return manufacturer


def get_pci_device_name(device_id):
    _, name = _find_names(device_id, PCI_DATABASE_PATHS)
    return name


def get_usb_device_name(device_id):
    _, name = _find_names(device_id, USB_DATABASE_PATHS)
    return name


def get_device_info(device_id, device_type):
    if device_type == "PCI":
        manufacturer, name = _find_names(device_id, PCI_DATABASE_PATHS)
    elif device_type == "USB":
        manufacturer, name = _find_names(device_id, USB_DATABASE_PATHS)
    else:
        manufacturer = "Unknown"
        name = "Unknown"

    return {
        "id": device_id,
        "manufacturer": manufacturer,
        "name": name,
        "type": device_type,
    }
