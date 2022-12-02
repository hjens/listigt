from pathlib import Path

from todo_list.todo_list import TodoItem
from todo_list.tree import TreeNode
from ui import ui
from view_model import view_model

SAVE_FILE = Path("small_test.txt")


def main():
    with open(SAVE_FILE) as f:
        tree = TreeNode.from_string(f.read(), TodoItem.tree_node_from_str)
    vm = view_model.ViewModel(tree, SAVE_FILE)
    ui.start_ui(vm)

if __name__ == "__main__":
    main()