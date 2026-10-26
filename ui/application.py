import gi

gi.require_version("Adw", "1")

from gi.repository import Adw

from ui.main_window import MainWindow


class DeviceWizardApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.github.devicewizard")

    def do_activate(self):
        window = self.props.active_window

        if window is None:
            window = MainWindow(application=self)

        window.present()


app = DeviceWizardApplication()
app.run(None)