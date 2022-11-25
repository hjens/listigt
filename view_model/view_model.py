from typing import List, Optional

from todo_list import todo_list
from todo_list.todo_list import TodoItem
from todo_list.tree import TreeNode


class ViewModel:
    def __init__(self, todo_list: todo_list.TodoList):
        self.todo_list = todo_list
        self.selected_node: Optional[TreeNode] = None
        self._is_inserting = False

        if todo_list.items:
            self.selected_node = todo_list.items[0]

    def item_titles(self) -> List[str]:
        def text_for_item(item):
            indent = " " * item.level * 2
            text = item.data.text
            if item == self.selected_node:
                return f"► {indent}{text}"
            return f"- {indent}{text}"

        lines = [
            text_for_item(item)
            for item in self.todo_list.gen_all_items()
        ]
        return lines

    def select_next(self):
        self.selected_node = self.todo_list.node_after(self.selected_node)

    def select_previous(self):
        self.selected_node = self.todo_list.node_before(self.selected_node)

    def start_insert(self):
        self._is_inserting = True

    def insertion_index(self) -> int:
        for index, item in enumerate(self.todo_list.gen_all_items()):
            if item == self.selected_node:
                return index + 1
        return 0

    @property
    def is_inserting(self):
        return self._is_inserting

    def insert_item(self, item_text: str):
        new_node = TreeNode(data=TodoItem(item_text))
        self.todo_list.add_item_after(item=self.selected_node, new_item=new_node)
        self._is_inserting = False
