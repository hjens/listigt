from typing import Any, Callable

import pytermgui as ptg
from pytermgui import HorizontalAlignment

from view_model import view_model


class NewItemInput(ptg.InputField):
    def __init__(
        self,
        on_submit: Callable[[str], None],
        on_cancel: Callable[[None], None],
        **attrs: Any
    ):
        super().__init__(**attrs)
        self.prompt = "New item: "
        self.on_submit = on_submit
        self.on_cancel = on_cancel

    def handle_key(self, key: str) -> bool:
        if super().handle_key(key):
            return True

        if key in ("å", "ä", "ö"):
            self.insert_text(key)
            return True
        if key == ptg.keys.ENTER:
            self.on_submit(self.value)
            self.delete_back(len(self.value))
            return True
        if key == ptg.keys.ESC:
            self.on_cancel()
            self.delete_back(len(self.value))
            return True
        return False


class TodoItemTree(ptg.Container):
    def __init__(self, vm: view_model.ViewModel, **attrs: Any):
        super().__init__(**attrs)
        self._view_model = vm
        self._create_widgets()

        def on_new_item_submit(text):
            self._view_model.insert_item(text)
            self._update_widgets()

        def on_new_item_cancel():
            self._view_model.cancel_insert()
            self._update_widgets()

        self.input_field = NewItemInput(
            on_submit=on_new_item_submit, on_cancel=on_new_item_cancel
        )

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
            self._widgets.insert(self._view_model.index_of_selected_node() + 1, self.input_field)
            self._update_widgets()
            return True
        elif key == "x":
            self._view_model.delete_item()
            self._update_widgets()
            return True
        elif key == "l":
            self._view_model.set_as_root(self._view_model.selected_node)
            self._update_widgets()
            return True
        elif key == "h":
            self._view_model.move_root_upwards()
            self._update_widgets()
            return True

        return False

    def _create_widgets(self):
        widgets = [
            ptg.Label(item, parent_align=HorizontalAlignment.LEFT)
            for item in self._view_model.item_titles()
        ]
        self.set_widgets(widgets)

    def _update_widgets(self):
        item_titles = self._view_model.item_titles()
        for index, widget in enumerate(self._widgets):
            if not isinstance(widget, ptg.Label):
                continue
            if index < len(item_titles):
                widget.value = item_titles[index]
            else:
                widget.value = ""

        has_input_field =  any([isinstance(w, ptg.InputField) for w in self._widgets])
        if has_input_field and not self._view_model.is_inserting:
            self._create_widgets()
