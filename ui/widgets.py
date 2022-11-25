from typing import Any

import pytermgui as ptg
from pytermgui import HorizontalAlignment

from view_model import view_model


class NewItemInput(ptg.InputField):
    def __init__(self, callback, **attrs: Any):
        super().__init__(**attrs)
        self.prompt = "New item: "
        self.callback = callback

    def handle_key(self, key: str) -> bool:
        if super().handle_key(key):
            return True

        if key in ("å", "ä", "ö"):
            self.insert_text(key)
            return True
        if key == ptg.keys.ENTER:
            self.callback(self.value)
            self.delete_back(len(self.value))
            return True
        return False


class TodoItemTree(ptg.Container):
    def __init__(self, vm: view_model.ViewModel, **attrs: Any):
        super().__init__(**attrs)
        self._view_model = vm
        self._update_widgets()

        def on_new_item_submit(text):
            self._view_model.insert_item(text)
            self._update_widgets()
        self.input_field = NewItemInput(on_new_item_submit)

    def handle_key(self, key: str) -> bool:
        if super().handle_key(key):
            return True

        if self._view_model.is_inserting:
            return self.input_field.handle_key(key)

        if key == "j":
            self._view_model.select_next()
            self._update_widgets()
            return True
        elif key == "k":
            self._view_model.select_previous()
            self._update_widgets()
            return True
        elif key == "n":
            self._view_model.start_insert()
            self._update_widgets()
            return True

        return False

    def _update_widgets(self):
        widgets = [
            ptg.Label(item, parent_align=HorizontalAlignment.LEFT)
            for item in self._view_model.item_titles()
        ]
        if self._view_model.is_inserting:
            widgets.insert(self._view_model.insertion_index(), self.input_field)
        self.set_widgets(widgets)
