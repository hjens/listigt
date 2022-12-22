import pytermgui as ptg

from listigt.utils.optional import Optional


class HelpWindow(ptg.Window):
    def __init__(self, manager: ptg.WindowManager):
        super().__init__()
        self._visible = False
        self._manager = manager
        self.set_widgets(["Hej"])
        self._alert: Optional[ptg.Window] = Optional.none()

    def show(self):
        self._alert = Optional.some(self._manager.alert(self))
        self._visible = True

    def handle_key(self, key: str) -> bool:
        if not self._visible:
            return False

        if key == ptg.keys.ESC:
            self._visible = False
            self._manager.remove(self._alert.value())
            self._alert = Optional.none()
            return True