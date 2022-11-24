from typing import List

from todo_list import tree


class ViewModel:
    def __init__(self, todo_list: List[tree.TreeNode]):
        self.todo_list = todo_list

    def item_titles(self) -> List[str]:
        return [i.data.text for i in self.todo_list]