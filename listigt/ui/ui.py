import pytermgui as ptg
from pytermgui import VerticalAlignment

from listigt.ui.search_field import SearchInput
from listigt.ui.todo_item_tree import TodoItemTree
from listigt.view_model import view_model
from listigt.ui.help_window import HelpWindow


def _define_layout() -> ptg.Layout:
    layout = ptg.Layout()

    layout.add_slot("Body")
    layout.add_break()
    layout.add_slot("Footer", height=3)

    return layout


def start_ui(vm: view_model.ViewModel):
    with ptg.WindowManager() as manager:
        manager.layout = _define_layout()
        vm.set_window_height(manager.terminal.height - 8)

        search_input = SearchInput(vm)
        todo_item_tree = TodoItemTree(vm, search_input)
        help_window = HelpWindow(manager)

        body_window = ptg.Window(
            todo_item_tree,
            vertical_align=VerticalAlignment.TOP,
            assign="body",
        )

        manager.add(body_window, animate=False)

        footer_window = ptg.Window(search_input, assign="footer")

        manager.add(footer_window, animate=False)

        def handle_key(key):
            if help_window.handle_key(key):
                return True
            if todo_item_tree.handle_key(key):
                return True
            if key == "q":
                manager.stop()
            if key == "?":
                help_window.show()

        manager.handle_key = handle_key
