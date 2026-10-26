import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("Device Wizard")
        self.set_default_size(900, 600)

        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
        )

        content.set_halign(Gtk.Align.CENTER)
        content.set_valign(Gtk.Align.CENTER)

        title = Gtk.Label(label="Device Wizard")
        title.add_css_class("title-1")

        scan_button = Gtk.Button(label="Scan Devices")

        content.append(title)
        content.append(scan_button)

        self.set_content(content)