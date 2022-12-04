import copy
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from todo_list.todo_list import TodoItem
from todo_list.tree import TreeNode, FilterFunction


@dataclass
class ListItem:
    text: str
    indentation_level: int
    is_selected: bool
    has_children: bool
    is_completed: bool
    is_collapsed: bool


class ViewModel:
    def __init__(self, tree_root: TreeNode, save_file: Path):
        self._save_file = save_file
        self.tree_root = tree_root
        self.selected_node: Optional[TreeNode] = None
        self._is_inserting = False
        self._cut_item: Optional[TreeNode] = None
        self._item_being_edited: Optional[TreeNode] = None
        self.hide_complete = False

        self.set_window_height(0)

        if self.tree_root.children:
            self.selected_node = self.tree_root.first_child()

    def save_to_file(self):
        with open(self._save_file, "w") as f:
            f.write("\n".join([str(item) for item in self.tree_root.root().children]))

    def set_window_height(self, height: int):
        self._num_items_on_screen = height
        self._first_item_on_screen = 0
        self._last_item_on_screen = self._num_items_on_screen

    @property
    def num_items_on_screen(self) -> int:
        return self._num_items_on_screen

    def list_items(self) -> List[ListItem]:
        def list_item_from_node(node):
            return ListItem(
                text=node.data.text,
                indentation_level=node.level - self.tree_root.level - 1,
                is_selected=node == self.selected_node,
                has_children=node.has_children(),
                is_completed=node.data.complete,
                is_collapsed=node.data.collapsed,
            )

        items = [list_item_from_node(node) for node in self._all_visible_nodes()]
        self._update_scrolling(len(items))
        return items[self._first_item_on_screen : self._last_item_on_screen]

    def list_title(self) -> str:
        if self.tree_root == self.tree_root.root():
            return "Toppnivå"
        return self.tree_root.data.text

    def toggle_hide_complete(self):
        self.hide_complete = not self.hide_complete

    def select_next(self):
        self.selected_node = self.tree_root.node_after(
            self.selected_node, self._make_filter_func()
        )

    def select_previous(self):
        self.selected_node = self.tree_root.node_before(
            self.selected_node, self._make_filter_func()
        )

    def select_bottom(self):
        nodes_list = list(self._all_visible_nodes())
        if len(nodes_list) >= self._last_item_on_screen - 1:
            self.selected_node = nodes_list[self._last_item_on_screen - 1]

    def select_top(self):
        nodes_list = list(self._all_visible_nodes())
        if len(nodes_list) >= self._first_item_on_screen:
            self.selected_node = nodes_list[self._first_item_on_screen]

    def select_middle(self):
        nodes_list = list(self._all_visible_nodes())
        middle_index = (self._first_item_on_screen + self._last_item_on_screen) // 2
        if len(nodes_list) >= middle_index:
            self.selected_node = nodes_list[middle_index]

    def set_as_root(self, node: Optional[TreeNode]):
        if node is None:
            return

        self.tree_root = node
        if self.tree_root.has_children():
            self.selected_node = self.tree_root.first_child()
        else:
            self.selected_node = None

    def move_root_upwards(self):
        if self.tree_root.parent:
            self.selected_node = self.tree_root
            self.tree_root = self.tree_root.parent
            self._first_item_on_screen = self.index_of_selected_node()
            self._last_item_on_screen = (
                self._first_item_on_screen + self._num_items_on_screen
            )

    def toggle_collapse_node(self):
        if self.selected_node:
            self.selected_node.data.collapsed = not self.selected_node.data.collapsed
        self.save_to_file()

    def start_insert(self):
        self._is_inserting = True

    def cancel_insert(self):
        self._is_inserting = False

    @property
    def is_inserting(self):
        return self._is_inserting

    def insert_item(self, item_text: str):
        new_node = TreeNode(data=TodoItem(item_text))
        if self.selected_node:
            self.selected_node.add_sibling(new_node)
        else:
            self.tree_root.add_child(new_node)
        self._is_inserting = False
        self.selected_node = new_node
        self._last_item_on_screen += 1

        self.save_to_file()

    def start_edit(self):
        if self.selected_node:
            self._item_being_edited = copy.deepcopy(self.selected_node)

    def cancel_edit(self):
        self._item_being_edited = None

    def finish_edit(self, new_text: str):
        assert self.is_editing
        self.selected_node.data.text = new_text
        self._item_being_edited = None
        self.save_to_file()

    @property
    def is_editing(self):
        return self._item_being_edited is not None

    def toggle_complete(self):
        def set_complete(node):
            node.data.complete = True

        if self.selected_node is None:
            return

        if not self.selected_node.data.complete:
            self.selected_node.apply_to_self_and_children(set_complete)
        else:
            self.selected_node.data.complete = False

        self.save_to_file()

    def index_of_selected_node(self) -> int:
        for index, item in enumerate(self._all_visible_nodes()):
            if item == self.selected_node:
                return index
        return 0

    def delete_item(self):
        node_to_remove = self.selected_node
        if node_to_remove is not None:
            self._cut_item = node_to_remove
            self.select_previous()
            self.tree_root.remove_node(node_to_remove)
            if not self.tree_root.has_children():
                self.selected_node = None

        self.save_to_file()

    def paste_item(self):
        if self.selected_node:
            self.selected_node.add_sibling(self._cut_item)
        else:
            self.tree_root.add_child(self._cut_item)
        self._cut_item = None

        self.save_to_file()

    def _update_scrolling(self, num_lines: int):
        if num_lines <= self._num_items_on_screen:
            self._first_item_on_screen = 0
            self._last_item_on_screen = num_lines

        selection_index = self.index_of_selected_node()
        if selection_index < self._first_item_on_screen:
            self._first_item_on_screen = selection_index
            self._last_item_on_screen = min(
                self._first_item_on_screen + self._num_items_on_screen, num_lines
            )
        elif selection_index >= self._last_item_on_screen:
            self._last_item_on_screen = selection_index + 1
            self._first_item_on_screen = max(
                0, self._last_item_on_screen - self._num_items_on_screen
            )

    def _all_visible_nodes(self):
        return self.tree_root.gen_all_nodes_with_condition(self._make_filter_func())

    def _make_filter_func(self) -> FilterFunction:
        def filter_func(node: TreeNode) -> bool:
            # Always hide completed items if hide_complete is set
            if self.hide_complete and node.data.complete:
                return False
            # Hide children of collapsed nodes
            if node.parent and node.parent.data.collapsed:
                return False
            # Make sure we hide all children of hidden nodes
            if node.parent and not filter_func(node.parent):
                return False
            return True

        return filter_func
