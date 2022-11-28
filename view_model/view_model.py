from dataclasses import dataclass
from typing import List, Optional

from todo_list.todo_list import TodoItem
from todo_list.tree import TreeNode


@dataclass
class ListItem:
    text: str
    indentation_level: int
    is_selected: bool
    has_children: bool
    is_completed: bool


class ViewModel:
    def __init__(self, tree_root: TreeNode):
        self.tree_root: TreeNode = tree_root
        self.selected_node: Optional[TreeNode] = None
        self._is_inserting = False

        self.set_window_height(32)  # TODO: this should not be hardcoded

        if tree_root.children:
            self.selected_node = tree_root.first_child()

    def set_window_height(self, height: int):
        self._num_items_on_screen = height
        self._first_item_on_screen = 0
        self._last_item_on_screen = self._num_items_on_screen

    def list_items(self) -> List[ListItem]:
        def list_item_from_node(node):
            return ListItem(
                text=node.data.text,
                indentation_level=node.level - self.tree_root.level,
                is_selected=node == self.selected_node,
                has_children=node.has_children(),
                is_completed=node.data.complete,
            )

        items = [list_item_from_node(node) for node in self.tree_root.gen_all_nodes()]
        self._update_scrolling(len(items))
        return items[self._first_item_on_screen : self._last_item_on_screen]

    def list_title(self) -> str:
        if self.tree_root == self.tree_root.root():
            return "Toppnivå"
        return self.tree_root.data.text

    def select_next(self):
        self.selected_node = self.tree_root.node_after(self.selected_node)

    def select_previous(self):
        self.selected_node = self.tree_root.node_before(self.selected_node)

    def set_as_root(self, node):
        self.tree_root = node
        if self.tree_root.children:
            self.selected_node = self.tree_root.first_child()

    def move_root_upwards(self):
        if self.tree_root.parent:
            self.selected_node = self.tree_root
            self.tree_root = self.tree_root.parent
            self._first_item_on_screen = self.index_of_selected_node()
            self._last_item_on_screen = (
                self._first_item_on_screen + self._num_items_on_screen
            )

    def start_insert(self):
        self._is_inserting = True

    def cancel_insert(self):
        self._is_inserting = False

    def toggle_completed(self):
        self.selected_node.data.complete = not self.selected_node.data.complete

    def index_of_selected_node(self) -> int:
        for index, item in enumerate(self.tree_root.gen_all_nodes()):
            if item == self.selected_node:
                return index
        return 0

    @property
    def is_inserting(self):
        return self._is_inserting

    def insert_item(self, item_text: str):
        new_node = TreeNode(data=TodoItem(item_text))
        self.selected_node.add_sibling(new_node)
        self._is_inserting = False

    def delete_item(self):
        node_to_remove = self.selected_node
        self.select_previous()
        self.tree_root.remove_node(node_to_remove)

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
