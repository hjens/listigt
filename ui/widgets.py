from typing import Any, Callable

import pytermgui as ptg
from pytermgui import HorizontalAlignment

from view_model import view_model
from view_model.view_model import ListItem


class NewItemInput(ptg.InputField):
    def __init__(
        self,
        on_submit: Callable[[str], None],
        on_cancel: Callable[[None], None],
        **attrs: Any,
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
        self._item_labels = [
            ptg.Label(
                self._text_for_list_item(item), parent_align=HorizontalAlignment.LEFT
            )
            for item in self._view_model.list_items()
        ]
        self._title_label = ptg.Label(
            vm.list_title(), parent_align=HorizontalAlignment.LEFT
        )
        self.set_widgets([self._title_label, *self._item_labels])

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
        if self._view_model.is_inserting:
            return self.input_field.handle_key(key)

        key_handlers = {
            "j": lambda: self._view_model.select_next(),
            "k": lambda: self._view_model.select_previous(),
            "n": lambda: self._view_model.start_insert(),
            "x": lambda: self._view_model.delete_item(),
            "l": lambda: self._view_model.set_as_root(self._view_model.selected_node),
            "h": lambda: self._view_model.move_root_upwards(),
            ptg.keys.ENTER: lambda: self._view_model.toggle_completed(),
        }

        if key in key_handlers:
            key_handlers[key]()
            self._update_widgets()
            return True

        return False

    def _update_widgets(self):
        list_items = self._view_model.list_items()
        for index, label in enumerate(self._item_labels):
            if index < len(list_items):
                label.value = self._text_for_list_item(list_items[index])
            else:
                label.value = ""

        self._title_label.value = f"[primary]{self._view_model.list_title().upper()}"

        has_input_field = any([isinstance(w, ptg.InputField) for w in self._widgets])
        if has_input_field and not self._view_model.is_inserting:
            self.set_widgets([w for w in self._widgets if w != self.input_field])
        elif self._view_model.is_inserting and not has_input_field:
            self._widgets.insert(
                self._view_model.index_of_selected_node() + 2, self.input_field
            )

    def _text_for_list_item(self, item: ListItem) -> str:
        indent = "  " * item.indentation_level
        highlighted = (item.is_selected and not self._view_model.is_inserting)
        style = "[inverse]" if highlighted else ""
        symbol = "▼" if item.has_children else "•"
        completed_style = "[strikethrough]" if item.is_completed else ""
        # ►
        return indent + style + completed_style + symbol + " " + item.text
