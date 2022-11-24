from ui import ui
from view_model import view_model
from todo_list import todo_list


def main():
    filename = "small_test.txt"
    with open(filename) as f:
        saved_todo_list = todo_list.TodoList.from_string(f.read(), todo_list.TodoItem.tree_node_from_str)
    vm = view_model.ViewModel(saved_todo_list)
    ui.start_ui(vm)

if __name__ == "__main__":
    main()