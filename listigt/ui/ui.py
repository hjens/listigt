import pytermgui as ptg
from pytermgui import VerticalAlignment

from listigt.ui.todo_item_tree import TodoItemTree
from listigt.view_model import view_model
from listigt.ui.help_window import HelpWindow
from listigt.ui.footer_window import FooterWindow


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

        footer_window = FooterWindow(vm, assign="footer")
        todo_item_tree = TodoItemTree(vm)
        help_window = HelpWindow(manager)

        body_window = ptg.Window(
            todo_item_tree,
            vertical_align=VerticalAlignment.TOP,
            assign="body",
        )

        manager.add(body_window, animate=False)

        manager.add(footer_window, animate=False)

        def handle_key(key):
            key_handled = False
            if todo_item_tree.handle_key(key):
                key_handled = True
            elif footer_window.handle_key(key):
                key_handled = True
            elif help_window.handle_key(key):
                key_handled = True
            elif key == "q":
                manager.stop()
                key_handled = True
            elif key == "?":
                help_window.show()
                key_handled = True

            todo_item_tree.post_handle_key()

            return key_handled

        manager.handle_key = handle_key
