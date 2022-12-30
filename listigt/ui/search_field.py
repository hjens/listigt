from typing import Any

import pyperclip
import pytermgui as ptg

from listigt.view_model import view_model


class SearchInput(ptg.InputField):
    def __init__(
        self,
        view_model: view_model.ViewModel,
        **attrs: Any,
    ):
        super().__init__(**attrs)
        self._default_prompt = "Press / to search"
        self.prompt = self._default_prompt
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
        if key == ptg.keys.ENTER:
            self._view_model.finish_search()
            self.clear_text()
            return True
        if key == ptg.keys.UP:
            self._view_model.select_previous_search_result()
            return True
        if key == ptg.keys.DOWN:
            self._view_model.select_next_search_result()
            return True
        if key == ptg.keys.ESC:  # TODO: do not use hardcoded values
            self._view_model.cancel_search()
            self.clear_text()
            return True
        return False

    def _on_type(self):
        self._view_model.update_search(self.value)

    def clear_text(self):
        self.delete_back(len(self.value))
        self.prompt = self._default_prompt
        self.select()
