import os
import subprocess


SCAN_TIMEOUT = 10


class DeviceScanError(RuntimeError):
    """Не удалось получить список устройств системной командой."""


def _run_scan(command):
    # Парсер ожидает английские подписи, например "Kernel driver in use".
    environment = os.environ.copy()
    environment["LC_ALL"] = "C"
    command_name = command[0]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=SCAN_TIMEOUT,
            env=environment,
        )
    except FileNotFoundError as error:
        raise DeviceScanError(
            f"Команда {command_name} не найдена. Установите пакет "
            f"{'pciutils' if command_name == 'lspci' else 'usbutils'}."
        ) from error
    except subprocess.TimeoutExpired as error:
        raise DeviceScanError(
            f"Команда {command_name} не завершилась за {SCAN_TIMEOUT} секунд."
        ) from error
    except OSError as error:
        raise DeviceScanError(
            f"Не удалось запустить команду {command_name}: {error}"
        ) from error

    if result.returncode != 0:
        details = result.stderr.strip() or "Причина не указана."
        raise DeviceScanError(
            f"Команда {command_name} завершилась с кодом "
            f"{result.returncode}: {details}"
        )

    return result.stdout


def scan_pci_devices():
    return _run_scan(["lspci", "-nn", "-k"])


def scan_usb_devices():
    return _run_scan(["lsusb"])
