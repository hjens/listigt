from ui import ui
from todo_list import tree, todo_list
from view_model import view_model


def main():
    filename = "small_test.txt"
    with open(filename) as f:
        todo_items = tree.tree_nodes_from_string(f.read(), todo_list.TodoItem.tree_node_from_str)
    vm = view_model.ViewModel(todo_items)
    ui.start_ui(vm)

if __name__ == "__main__":
    main()