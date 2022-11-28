from pathlib import Path

from ui import ui
from view_model import view_model
from todo_list import todo_list

SAVE_FILE = Path("small_test.txt")


def main():
    vm = view_model.ViewModel(SAVE_FILE)
    ui.start_ui(vm)

if __name__ == "__main__":
    main()