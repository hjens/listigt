from dataclasses import dataclass
from pathlib import Path
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
    is_collapsed: bool


class ViewModel:
    def __init__(self, save_file: Path):
        self._save_file = save_file
        self.tree_root: TreeNode = self.load_from_file()
        self.selected_node: Optional[TreeNode] = None
        self._is_inserting = False

        self.set_window_height(0)

        if self.tree_root.children:
            self.selected_node = self.tree_root.first_child()

    def save_to_file(self):
        with open(self._save_file, "w") as f:
            f.write("\n".join([str(item) for item in self.tree_root.root().children]))

    def load_from_file(self) -> TreeNode:
        with open(self._save_file) as f:
            return TreeNode.from_string(f.read(), TodoItem.tree_node_from_str)

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

        collapsed_filter = lambda node: not node.data.collapsed
        items = [
            list_item_from_node(node)
            for node in self.tree_root.gen_all_nodes_with_condition(collapsed_filter)
        ]
        self._update_scrolling(len(items))
        return items[self._first_item_on_screen : self._last_item_on_screen]

    def list_title(self) -> str:
        if self.tree_root == self.tree_root.root():
            return "Toppnivå"
        return self.tree_root.data.text

    def select_next(self):
        collapsed_filter = lambda node: not node.data.collapsed
        self.selected_node = self.tree_root.node_after(
            self.selected_node, collapsed_filter
        )

    def select_previous(self):
        collapsed_filter = lambda node: not node.data.collapsed
        self.selected_node = self.tree_root.node_before(
            self.selected_node, collapsed_filter
        )

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

    def start_insert(self):
        self._is_inserting = True

    def cancel_insert(self):
        self._is_inserting = False

    def toggle_completed(self):
        def toogle_node(node):
            node.data.complete = not node.data.complete

        if self.selected_node is not None:
            self.selected_node.apply_to_children(toogle_node)

        self.save_to_file()

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
        if self.selected_node:
            self.selected_node.add_sibling(new_node)
        else:
            self.tree_root.add_child(new_node)
        self._is_inserting = False
        self.selected_node = new_node
        self._last_item_on_screen += 1

        self.save_to_file()

    def delete_item(self):
        node_to_remove = self.selected_node
        if node_to_remove is not None:
            self.select_previous()
            self.tree_root.remove_node(node_to_remove)

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
