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

        manager.add(ptg.Window(
            widgets.TodoItemTree(vm),
            assign="body"
        ))
