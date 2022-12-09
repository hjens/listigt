from pathlib import Path

from config import config
from todo_list.todo_list import TodoItem
from todo_list.tree import TreeNode
from ui import ui
from view_model import view_model

SAVE_FILE = Path("small_test.txt")


def main():
    config_manager = config.ConfigManager()
    with open(SAVE_FILE) as f:
        tree = TreeNode.from_string(f.read(), TodoItem.tree_node_from_str)
    vm = view_model.ViewModel(
        tree_root=tree, save_file=SAVE_FILE, config_manager=config_manager
    )
    ui.start_ui(vm)


if __name__ == "__main__":
    main()
