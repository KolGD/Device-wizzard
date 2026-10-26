import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core import device_info


class DeviceInfoTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.database = Path(self.directory.name) / "devices.ids"
        self.database.write_text(
            "# Example system ID database\n"
            "1234  Example manufacturer\n"
            "\t1111  Another model\n"
            "\t\tabcd  Subsystem, not a device\n"
            "# A comment must not end the vendor block\n"
            "\n"
            "\t5678  Example model\n"
            "9999  Other manufacturer\n"
            "\tabcd  Belongs to another vendor\n"
            "C 03  Device class\n",
            encoding="utf-8",
        )
        for setting in ("PCI_DATABASE_PATHS", "USB_DATABASE_PATHS"):
            patcher = patch.object(device_info, setting, (str(self.database),))
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_both_bus_types_skip_comments_and_find_device_in_vendor_block(self):
        for bus_type in ("PCI", "USB"):
            with self.subTest(bus_type=bus_type):
                info = device_info.get_device_info("1234:5678", bus_type)

                self.assertEqual(info["manufacturer"], "Example manufacturer")
                self.assertEqual(info["name"], "Example model")

    def test_subsystem_and_other_vendor_cannot_match_device(self):
        for bus_type in ("PCI", "USB"):
            with self.subTest(bus_type=bus_type):
                info = device_info.get_device_info("1234:abcd", bus_type)

                self.assertEqual(info["manufacturer"], "Example manufacturer")
                self.assertEqual(info["name"], "Unknown")

    def test_lookup_normalizes_case_and_spaces(self):
        self.database.write_text("abcd  Hex vendor\n\tefab  Hex model\n", encoding="utf-8")

        for bus_type in ("PCI", "USB"):
            with self.subTest(bus_type=bus_type):
                info = device_info.get_device_info(" ABCD : EFAB ", bus_type)

                self.assertEqual(info["manufacturer"], "Hex vendor")
                self.assertEqual(info["name"], "Hex model")

    def test_malformed_and_unknown_ids_are_safe(self):
        for device_id in (None, "", "1234", "1234:5678:9abc", "123:5678", "zzzz:5678", "ffff:ffff"):
            for bus_type in ("PCI", "USB"):
                with self.subTest(device_id=device_id, bus_type=bus_type):
                    info = device_info.get_device_info(device_id, bus_type)

                    self.assertEqual(info["manufacturer"], "Unknown")
                    self.assertEqual(info["name"], "Unknown")

    def test_missing_database_returns_unknown(self):
        missing = str(Path(self.directory.name) / "missing.ids")
        with patch.object(device_info, "PCI_DATABASE_PATHS", (missing,)):
            info = device_info.get_device_info("1234:5678", "PCI")

        self.assertEqual(info["manufacturer"], "Unknown")
        self.assertEqual(info["name"], "Unknown")

    def test_database_search_falls_back_when_first_path_is_missing(self):
        missing = str(Path(self.directory.name) / "missing.ids")
        with patch.object(device_info, "USB_DATABASE_PATHS", (missing, str(self.database))):
            info = device_info.get_device_info("1234:5678", "USB")

        self.assertEqual(info["manufacturer"], "Example manufacturer")
        self.assertEqual(info["name"], "Example model")


if __name__ == "__main__":
    unittest.main()
