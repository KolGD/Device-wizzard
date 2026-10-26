import importlib
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from core import device_scanner


class MainTests(unittest.TestCase):
    def test_import_does_not_scan_devices(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch.object(device_scanner, "scan_pci_devices") as pci_scan,
            patch.object(device_scanner, "scan_usb_devices") as usb_scan,
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            main_module = importlib.import_module("main")
            importlib.reload(main_module)

        # Restore imported function references after the scanner patches end.
        importlib.reload(main_module)
        pci_scan.assert_not_called()
        usb_scan.assert_not_called()
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")

    def test_pci_failure_still_lists_usb_devices_and_returns_failure(self):
        main_module = importlib.import_module("main")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch.object(
                main_module,
                "scan_pci_devices",
                side_effect=device_scanner.DeviceScanError("PCI unavailable"),
            ),
            patch.object(
                main_module,
                "scan_usb_devices",
                return_value="Bus 001 Device 002: ID 046d:c534 USB Receiver\n",
            ) as usb_scan,
            patch.object(main_module, "enrich_devices", side_effect=lambda devices, _: devices),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            exit_code = main_module.main()

        self.assertEqual(exit_code, 1)
        usb_scan.assert_called_once_with()
        self.assertIn("Found 1 USB devices", stdout.getvalue())
        self.assertIn("USB Receiver", stdout.getvalue())
        self.assertNotIn("Found 0 PCI devices", stdout.getvalue())
        self.assertIn("PCI unavailable", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
