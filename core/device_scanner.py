import subprocess


def scan_pci_devices():
    result = subprocess.run(
        ["lspci", "-nn", "-k"],
        capture_output=True,
        text=True
    )

    return result.stdout


def scan_usb_devices():
    result = subprocess.run(   
        ["lsusb"],
        capture_output=True,
        text=True
    )

    return result.stdout