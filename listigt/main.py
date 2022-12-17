import argparse
import atexit
from pathlib import Path

from listigt.config import config
from listigt.todo_list.todo_list import TodoItem
from listigt.todo_list.tree import TreeNode
from listigt.ui import ui
from listigt.view_model import view_model
from listigt.utils.optional import Optional


def main():
    args = _parse_args()

    config_manager = config.ConfigManager(save_file=args.save_file, config_file=args.config_file)
    tree = _read_saved_state(config_manager.save_file)
    vm = view_model.ViewModel(
        tree_root=tree, config_manager=config_manager
    )

    def exit_handler():
        config_manager.save_config()
        vm.save_to_file()

    atexit.register(exit_handler)

    ui.start_ui(vm)


def _read_saved_state(save_file: Path) -> TreeNode:
    save_file.parent.mkdir(exist_ok=True)

    if save_file.exists():
        with open(save_file) as f:
            return TreeNode.from_string(f.read(), TodoItem.tree_node_from_str)

    return TreeNode.from_string("", TodoItem.tree_node_from_str)



def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "save_file",
        type=Path,
        nargs="?",
        default=Optional.none(),
        help=f"Save file to use. Will override the default, which is {config.ConfigManager().save_file}."
    )
    parser.add_argument(
        "--config_file",
        type=Path,
        default=Optional.none(),
        required=False,
        help=f"Config file to use. Will override the default, which is {config.ConfigManager().config_file}"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
