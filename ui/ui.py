import pytermgui as ptg

from ui import widgets
from view_model import view_model


def _define_layout() -> ptg.Layout:
    layout = ptg.Layout()

    layout.add_slot("Header", height=1)
    layout.add_break()

    layout.add_slot("Body")

    return layout


def start_ui(vm: view_model.ViewModel):
    with ptg.WindowManager() as manager:
        manager.layout = _define_layout()

        manager.add(ptg.Window(
            "[blue]My test TUI", box="EMPTY"
        ))

        todo_item_tree = widgets.TodoItemTree(vm)

        manager.add(ptg.Window(
            todo_item_tree,
            assign="body"
        ))

        def handle_key(key):
            if key == "q":
                manager.stop()
            todo_item_tree.handle_key(key)
        manager.handle_key = handle_key
