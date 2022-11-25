from typing import List, Optional

from todo_list.todo_list import TodoItem
from todo_list.tree import TreeNode


class ViewModel:
    def __init__(self, tree_root: TreeNode):
        self.tree_root = tree_root
        self.selected_node: Optional[TreeNode] = None
        self._is_inserting = False

        if tree_root.children:
            self.selected_node = tree_root.first_child()

    def item_titles(self) -> List[str]:
        def text_for_item(item):
            indent = " " * item.level * 2
            text = item.data.text
            if item == self.selected_node:
                return f"► {indent}{text}"
            return f"- {indent}{text}"

        lines = [text_for_item(item) for item in self.tree_root.gen_all_nodes()]
        return lines

    def select_next(self):
        self.selected_node = self.tree_root.node_after(self.selected_node)

    def select_previous(self):
        self.selected_node = self.tree_root.node_before(self.selected_node)

    def start_insert(self):
        self._is_inserting = True

    def cancel_insert(self):
        self._is_inserting = False

    def insertion_index(self) -> int:
        for index, item in enumerate(self.tree_root.gen_all_nodes()):
            if item == self.selected_node:
                return index + 1
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
