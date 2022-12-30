from typing import Any

import pytermgui as ptg
from pytermgui import HorizontalAlignment

from listigt.ui.action import Action, action_for_key, ALL_ACTIONS
from listigt.ui.new_item_input import NewItemInput
from listigt.ui.search_field import SearchInput
from listigt.view_model import view_model
from listigt.view_model.view_model import ListItem


class TodoItemTree(ptg.Container):
    INDENT_SPACES = 3

    def __init__(
        self, vm: view_model.ViewModel, **attrs: Any
    ):
        super().__init__(**attrs)
        self._view_model = vm

        self._create_new_item_input_widget()
        self._create_edit_item_widget()
        self._create_default_label_widgets()
        self._setup_keyhandlers()

    def _setup_keyhandlers(self):
        self._key_handlers = {
            Action.SELECT_NEXT: self._view_model.select_next,
            Action.SELECT_PREVIOUS: self._view_model.select_previous,
            Action.SELECT_BOTTOM: self._view_model.select_bottom,
            Action.SELECT_TOP: self._view_model.select_top,
            Action.SELECT_MIDDLE: self._view_model.select_middle,
            Action.INSERT_AFTER: self._view_model.start_insert_after,
            Action.INSERT_BEFORE: self._view_model.start_insert_before,
            Action.DELETE_ITEM: self._view_model.delete_item,
            Action.SET_AS_ROOT: lambda: self._view_model.set_as_root(self._view_model.selected_node),
            Action.MOVE_ROOT_UP: self._view_model.move_root_upwards,
            Action.PASTE_ITEM_AFTER: self._view_model.paste_item,
            Action.PASTE_ITEM_BEFORE: lambda: self._view_model.paste_item(before=True),
            Action.EDIT_ITEM: self._view_model.start_edit,
            Action.TOGGLE_HIDE_COMPLETE: self._view_model.toggle_hide_complete_items,
            Action.UNDO: self._view_model.undo,
            Action.TOGGLE_COMPLETE: self._view_model.toggle_complete,
            Action.COLLAPSE: self._view_model.toggle_collapse_node,
        }

    def _create_edit_item_widget(self, value: str = ""):
        def on_edit_item_submit(text):
            self._view_model.finish_edit(text)
            self._update_widgets()

        def on_edit_item_cancel(text):
            self._view_model.cancel_edit()
            self._update_widgets()

        self.edit_item_field = NewItemInput(
            on_submit=on_edit_item_submit, on_cancel=on_edit_item_cancel, value=value
        )

    def _create_new_item_input_widget(self):
        def on_new_item_submit(text):
            self._view_model.insert_item(text)
            self._update_widgets()
            self._view_model.start_insert_after()
            self._update_widgets()

        def on_new_item_cancel(text):
            if text:
                self._view_model.insert_item(text)
            else:
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
            self._view_model.list_title()[0], parent_align=HorizontalAlignment.LEFT
        )
        self.set_widgets([self._title_label, *self._item_labels])
        self._update_widgets()

    def handle_key(self, key: str) -> bool:
        if self._view_model.is_searching:
            return False

        if self._view_model.is_inserting:
            return self.input_field.handle_key(key)
        if self._view_model.is_editing:
            return self.edit_item_field.handle_key(key)

        if action := action_for_key(key).value_or_none():
            if action in self._key_handlers:
                self._key_handlers[action]()
                self._update_widgets()
                return True

        return False

    def post_handle_key(self, key: str):
        if self._view_model.is_searching:
             #We need to manually update widgets when searching
            self._update_widgets()
        elif key == ALL_ACTIONS[Action.CANCEL_SEARCH].key:
            self._update_widgets()

    def on_resize(self):
        self._update_widgets()

    def _update_widgets(self):
        def update_texts_for_labels(list_items):
            for index, label in enumerate(self._item_labels):
                if index < len(list_items):
                    label.value = self._text_for_list_item(list_items[index])
                    label.padding = list_items[index].indentation_level * self.INDENT_SPACES
                    label.non_first_padding = 2
                else:
                    label.value = ""

            list_title, breadcrumbs = self._view_model.list_title()
            self._title_label.value = f"[gray]{breadcrumbs}[bold primary]{list_title}"

        def show_or_hide_input_field(list_items):
            input_field_visible = self.input_field in self._widgets

            if input_field_visible and not self._view_model.is_inserting:
                self.set_widgets([w for w in self._widgets if w != self.input_field])
            elif self._view_model.is_inserting and not input_field_visible:
                indent = self._view_model.insertion_indent()
                self.input_field.prompt = " " * indent * self.INDENT_SPACES + "• "

                self._widgets.insert(self._view_model.insertion_index(), self.input_field)
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

        highlighted = item.is_selected and not self._view_model.is_inserting
        style = "[inverse]" if highlighted else ""
        symbol = symbol_for_item(item)
        completed_style = "[strikethrough forestgreen]" if item.is_completed else ""
        search_style = "[yellow]" if item.is_search_result else ""
        return (
            style + completed_style + search_style + symbol + " " + item.text
        )
