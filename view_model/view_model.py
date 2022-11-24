from typing import List

from todo_list import todo_list


class ViewModel:
    def __init__(self, todo_list: todo_list.TodoList):
        self.todo_list = todo_list
        self.selection_index = 0

    def item_titles(self) -> List[str]:
        def text_for_item(item, index):
            indent = " " * item.level * 2
            text = item.data.text
            if index == self.selection_index:
                return f"► {indent}{text}"
            return f"- {indent}{text}"
        lines = [text_for_item(item, index) for index, item in enumerate(self.todo_list.gen_all_items())]
        return lines

    def select_next(self):
        self.selection_index += 1
        if self.selection_index >= len(self.item_titles()):
            self.selection_index = 0

    def select_previous(self):
        self.selection_index -= 1
        if self.selection_index < 0:
            self.selection_index = len(self.item_titles()) - 1