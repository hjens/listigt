import pytermgui as ptg
from pytermgui import VerticalAlignment

from ui import widgets
from view_model import view_model


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

        todo_item_tree = widgets.TodoItemTree(vm)

        body_window = ptg.Window(
            todo_item_tree,
            vertical_align=VerticalAlignment.TOP,
            assign="body",
        )

        manager.add(body_window, animate=False)

        footer_window = ptg.Window("Footer", assign="footer")

        manager.add(footer_window, animate=False)

        def handle_key(key):
            if todo_item_tree.handle_key(key):
                return True
            if key == "q":
                manager.stop()

        manager.handle_key = handle_key
