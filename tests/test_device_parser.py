import unittest
from unittest.mock import patch

from core import device_parser


class DeviceParserTests(unittest.TestCase):
    def test_pci_keeps_device_id_separate_from_class_and_revision(self):
        output = (
            "0000:00:02.0 VGA compatible controller [0300]: "
            "Intel Corporation Graphics [8086:1234] (rev 04)\n"
            "\tKernel driver in use: i915\n"
            "\tKernel modules: i915\n"
        )

        devices = device_parser.parse_pci_devices(output)

        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0]["address"], "0000:00:02.0")
        self.assertEqual(devices[0]["id"], "8086:1234")
        self.assertEqual(devices[0]["name"], "Intel Corporation Graphics")
        self.assertEqual(devices[0]["driver"], "i915")

    def test_malformed_pci_header_does_not_attach_its_driver_to_previous_device(self):
        output = (
            "00:02.0 VGA compatible controller [0300]: Graphics [8086:1234]\n"
            "unrecognized output\n"
            "\tKernel driver in use: wrong_driver\n"
            "00:14.0 USB controller [0c03]: USB controller [8086:5678]\n"
            "\tKernel driver in use: xhci_hcd\n"
        )

        devices = device_parser.parse_pci_devices(output)

        self.assertEqual(len(devices), 2)
        self.assertIsNone(devices[0]["driver"])
        self.assertEqual(devices[1]["driver"], "xhci_hcd")

    def test_usb_accepts_variable_whitespace_and_missing_name(self):
        output = (
            "Bus  001\tDevice 002:  ID 046d:c534 Logitech USB Receiver\n"
            "Bus 002 Device 003: ID 1234:abcd\n"
            "\ninvalid output\n"
            "Bus 002 Device 004: ID invalid Bad device\n"
        )

        devices = device_parser.parse_usb_devices(output)

        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0]["bus"], "001")
        self.assertEqual(devices[0]["device"], "002")
        self.assertEqual(devices[0]["id"], "046d:c534")
        self.assertEqual(devices[0]["name"], "Logitech USB Receiver")
        self.assertEqual(devices[1]["name"], "Unknown")

    def test_empty_scanner_output_is_safe(self):
        self.assertEqual(device_parser.parse_pci_devices("\n \n"), [])
        self.assertEqual(device_parser.parse_usb_devices("\n \n"), [])

    def test_enrichment_preserves_original_name_when_lookup_has_no_name(self):
        for missing_name in ("Unknown", "", None):
            with self.subTest(name=missing_name):
                devices = [{"id": "046d:c534", "name": "Logitech USB Receiver"}]
                info = {
                    "id": "046d:c534",
                    "name": missing_name,
                    "manufacturer": "Logitech, Inc.",
                    "type": "USB",
                }
                with patch.object(device_parser, "get_device_info", return_value=info):
                    result = device_parser.enrich_devices(devices, "USB")

                self.assertEqual(result[0]["name"], "Logitech USB Receiver")
                self.assertEqual(result[0]["manufacturer"], "Logitech, Inc.")
                self.assertEqual(result[0]["type"], "USB")

    def test_enrichment_uses_known_database_name(self):
        devices = [{"id": "8086:1234", "name": "Intel Corporation Device"}]
        info = {
            "id": "8086:1234",
            "name": "Example graphics controller",
            "manufacturer": "Intel Corporation",
            "type": "PCI",
        }
        with patch.object(device_parser, "get_device_info", return_value=info):
            result = device_parser.enrich_devices(devices, "PCI")

        self.assertEqual(result[0]["name"], "Example graphics controller")


if __name__ == "__main__":
    unittest.main()
