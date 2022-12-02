from typing import Any, Callable

import pyperclip
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
            self.on_cancel()
            self.delete_back(len(self.value))
            return True
        if key == ptg.keys.CTRL_V:
            self.insert_text(pyperclip.paste())
            return True
        return False


class TodoItemTree(ptg.Container):
    INDENT_SPACES = 3

    def __init__(self, vm: view_model.ViewModel, **attrs: Any):
        super().__init__(**attrs)
        self._view_model = vm

        self._create_new_item_input_widget()
        self._create_edit_item_widget()
        self._create_default_label_widgets()

    def _create_edit_item_widget(self, value: str = ""):
        def on_edit_item_submit(text):
            self._view_model.finish_edit(text)
            self._update_widgets()

        def on_edit_item_cancel():
            self._view_model.cancel_edit()
            self._update_widgets()

        self.edit_item_field = NewItemInput(
            on_submit=on_edit_item_submit, on_cancel=on_edit_item_cancel, value=value
        )

    def _create_new_item_input_widget(self):
        def on_new_item_submit(text):
            self._view_model.insert_item(text)
            self._update_widgets()

        def on_new_item_cancel():
            self._view_model.cancel_insert()
            self._update_widgets()

        self.input_field = NewItemInput(
            on_submit=on_new_item_submit, on_cancel=on_new_item_cancel
        )

    def _create_default_label_widgets(self):
        self._item_labels = [
            ptg.Label("", parent_align=HorizontalAlignment.LEFT)
            for _ in range(self._view_model.num_items_on_screen)
        ]
        self._title_label = ptg.Label(
            self._view_model.list_title(), parent_align=HorizontalAlignment.LEFT
        )
        self.set_widgets([self._title_label, *self._item_labels])
        self._update_widgets()

    def handle_key(self, key: str) -> bool:
        if self._view_model.is_inserting:
            return self.input_field.handle_key(key)
        if self._view_model.is_editing:
            return self.edit_item_field.handle_key(key)

        key_handlers = {
            "j": lambda: self._view_model.select_next(),
            "k": lambda: self._view_model.select_previous(),
            "L": lambda: self._view_model.select_bottom(),
            "H": lambda: self._view_model.select_top(),
            "M": lambda: self._view_model.select_middle(),
            "n": lambda: self._view_model.start_insert(),
            "x": lambda: self._view_model.delete_item(),
            "l": lambda: self._view_model.set_as_root(self._view_model.selected_node),
            "h": lambda: self._view_model.move_root_upwards(),
            "p": lambda: self._view_model.paste_item(),
            "e": lambda: self._view_model.start_edit(),
            ptg.keys.ENTER: lambda: self._view_model.toggle_completed(),
            ptg.keys.SPACE: lambda: self._view_model.toggle_collapse_node(),
        }

        if key in key_handlers:
            key_handlers[key]()
            self._update_widgets()
            return True

        return False

    def _update_widgets(self):
        def update_texts_for_labels(list_items):
            for index, label in enumerate(self._item_labels):
                if index < len(list_items):
                    label.value = self._text_for_list_item(list_items[index])
                else:
                    label.value = ""

            self._title_label.value = (
                f"[bold primary]{self._view_model.list_title().upper()}"
            )

        def show_or_hide_input_field(list_items):
            input_field_visible = self.input_field in self._widgets

            if input_field_visible and not self._view_model.is_inserting:
                self.set_widgets([w for w in self._widgets if w != self.input_field])
            elif self._view_model.is_inserting and not input_field_visible:
                try:
                    indent = list_items[
                        self._view_model.index_of_selected_node()
                    ].indentation_level
                except IndexError:
                    indent = 0
                self.input_field.prompt = " " * indent * self.INDENT_SPACES + "• "
                
                if self._view_model.selected_node is None:
                    self._widgets.insert(1, self.input_field)
                else:
                    self._widgets.insert(
                        self._view_model.index_of_selected_node() + 2, self.input_field
                    )
                self.set_widgets(self._widgets)
                self.input_field.select(0)

        def show_or_hide_edit_field(list_items):
            edit_field_visible = self.edit_item_field in self._widgets

            if edit_field_visible and not self._view_model.is_editing:
                # Need to rebuild everything since one label was removed when starting edit
                self._create_default_label_widgets()
            elif self._view_model.is_editing and not edit_field_visible:
                # Need to revuild the edit field because that seems to be the only way
                # to set a new value
                selected_item = list_items[self._view_model.index_of_selected_node()]
                self._create_edit_item_widget(value=selected_item.text)
                self.edit_item_field.prompt = (
                    " " * selected_item.indentation_level * self.INDENT_SPACES + "• "
                )
                edited_node_index = self._view_model.index_of_selected_node()
                self._widgets = (
                    self._widgets[: edited_node_index + 1]
                    + [self.edit_item_field]
                    + self._widgets[edited_node_index + 2 :]
                )
                self.set_widgets(self._widgets)
                self.edit_item_field.select(0)

        list_items = self._view_model.list_items()
        update_texts_for_labels(list_items)
        show_or_hide_input_field(list_items)
        show_or_hide_edit_field(list_items)

    def _text_for_list_item(self, item: ListItem) -> str:
        def symbol_for_item(item: ListItem) -> str:
            if not item.has_children:
                return "•"
            elif item.is_collapsed:
                return "►"
            return "▼"

        indent = " " * item.indentation_level * self.INDENT_SPACES
        highlighted = item.is_selected and not self._view_model.is_inserting
        style = "[inverse]" if highlighted else ""
        symbol = symbol_for_item(item)
        completed_style = "[strikethrough forestgreen]" if item.is_completed else ""
        return indent + style + completed_style + symbol + " " + item.text
