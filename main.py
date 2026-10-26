import sys

from core.device_parser import enrich_devices, parse_pci_devices, parse_usb_devices
from core.device_scanner import DeviceScanError, scan_pci_devices, scan_usb_devices


def main():
    exit_code = 0

    for device_type, scan, parse in (
        ("PCI", scan_pci_devices, parse_pci_devices),
        ("USB", scan_usb_devices, parse_usb_devices),
    ):
        try:
            raw_output = scan()
        except DeviceScanError as error:
            print(f"Scanning failed: {device_type}: {error}", file=sys.stderr)
            exit_code = 1
            continue

        devices = enrich_devices(parse(raw_output), device_type)
        for device in devices:
            print(device)
        print(f"Found {len(devices)} {device_type} devices")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
