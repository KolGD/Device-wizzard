from core.device_parser import (
    parse_pci_devices,
    parse_usb_devices,
    enrich_devices
)
from core.device_scanner import scan_pci_devices, scan_usb_devices


# PCI devices
pci_output = scan_pci_devices()
pci_devices = parse_pci_devices(pci_output)
pci_devices = enrich_devices(pci_devices, "PCI")

for device in pci_devices:
    print(device)

print(f"Found {len(pci_devices)} PCI devices")


# USB devices
usb_output = scan_usb_devices()
usb_devices = parse_usb_devices(usb_output)
usb_devices = enrich_devices(usb_devices, "USB")

for device in usb_devices:
    print(device)

print(f"Found {len(usb_devices)} USB devices")