from typing import List

from todo_list import tree


class ViewModel:
    def __init__(self, todo_list: List[tree.TreeNode]):
        self.todo_list = todo_list
        self.selection_index = 0

    def item_titles(self) -> List[str]:
        def text_for_item(item, index):
            if index == self.selection_index:
                return f"► {item}"
            return f"- {item}"
        lines = [text_for_item(item.data.text, index) for index, item in enumerate(self.todo_list)]
        return lines

    def select_next(self):
        self.selection_index += 1
        if self.selection_index >= len(self.item_titles()):
            self.selection_index = 0

    def select_previous(self):
        self.selection_index -= 1
        if self.selection_index < 0:
            self.selection_index = len(self.item_titles()) - 1
