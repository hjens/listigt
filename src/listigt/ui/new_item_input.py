from typing import Any, Callable

import pyperclip
import pytermgui as ptg


class NewItemInput(ptg.InputField):
    def __init__(
        self,
        on_submit: Callable[[str], None],
        on_cancel: Callable[[str], None],
        **attrs: Any,
    ):
        super().__init__(**attrs)
        self.prompt = "• "
        self.on_submit = on_submit
        self.on_cancel = on_cancel

    def handle_key(self, key: str) -> bool:
        if super().handle_key(key):
            return True

        if key in ("å", "ä", "ö", "Å", "Ä", "Ö"):
            self.insert_text(key)
            return True
        if key == ptg.keys.ENTER:
            self.on_submit(self.value)
            self.delete_back(len(self.value))
            return True
        if key == ptg.keys.ESC:
            self.on_cancel(self.value)
            self.delete_back(len(self.value))
            return True
        if key == ptg.keys.CTRL_V:
            self.insert_text(pyperclip.paste())
            return True
        return False
