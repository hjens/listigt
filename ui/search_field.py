from typing import Any

import pyperclip
import pytermgui as ptg

from view_model.view_model import ViewModel


class SearchInput(ptg.InputField):
    def __init__(
        self,
        view_model: ViewModel,
        **attrs: Any,
    ):
        super().__init__(**attrs)
        self.prompt = "Search: "
        self._view_model = view_model

    def handle_key(self, key: str) -> bool:
        if not self._view_model.is_searching:
            return False

        if super().handle_key(key):
            self._on_type()
            return True

        if key in ("å", "ä", "ö", "Å", "Ä", "Ö"):
            self.insert_text(key)
            self._on_type()
            return True
        if key == ptg.keys.CTRL_V:
            self.insert_text(pyperclip.paste())
            return True
        return False

    def _on_type(self):
        self._view_model.update_search(self.value)
