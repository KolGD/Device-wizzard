import subprocess
import unittest
from unittest.mock import patch

from core import device_scanner


class DeviceScannerTests(unittest.TestCase):
    def test_scans_return_output_and_force_stable_locale(self):
        for scan, command in (
            (device_scanner.scan_pci_devices, ["lspci", "-nn", "-k"]),
            (device_scanner.scan_usb_devices, ["lsusb"]),
        ):
            with self.subTest(command=command):
                result = subprocess.CompletedProcess(command, 0, stdout="device output\n", stderr="")
                with patch.object(device_scanner.subprocess, "run", return_value=result) as run:
                    self.assertEqual(scan(), "device output\n")

                args, kwargs = run.call_args
                self.assertEqual(args[0], command)
                self.assertEqual(kwargs["env"]["LC_ALL"], "C")
                self.assertGreater(kwargs["timeout"], 0)

    def test_nonzero_exit_surfaces_stderr_as_scan_error(self):
        result = subprocess.CompletedProcess(["lsusb"], 1, stdout="", stderr="unable to initialize libusb")
        with patch.object(device_scanner.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(device_scanner.DeviceScanError, "libusb"):
                device_scanner.scan_usb_devices()

    def test_missing_command_timeout_and_os_errors_are_scan_errors(self):
        for error in (
            FileNotFoundError("lspci"),
            subprocess.TimeoutExpired(["lspci"], 10),
            OSError("cannot execute command"),
        ):
            with self.subTest(error=type(error).__name__):
                with patch.object(device_scanner.subprocess, "run", side_effect=error):
                    with self.assertRaises(device_scanner.DeviceScanError):
                        device_scanner.scan_pci_devices()


if __name__ == "__main__":
    unittest.main()
