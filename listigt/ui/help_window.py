import pytermgui as ptg
from pytermgui import HorizontalAlignment

from listigt.ui.action import Action, ALL_ACTIONS, display_text_for_key


class HelpWindow(ptg.Window):
    def __init__(self, manager: ptg.WindowManager):
        super().__init__()
        self._visible = False
        self._manager = manager
        self.width = 50

        title = f"[primary bold]Help"
        actions = [
            Action.SELECT_NEXT,
            Action.SELECT_PREVIOUS,
            Action.SELECT_BOTTOM,
            Action.SELECT_TOP,
            Action.SELECT_MIDDLE,
            None,
            Action.SET_AS_ROOT,
            Action.MOVE_ROOT_UP,
            Action.COLLAPSE,
            None,
            Action.INSERT_BEFORE,
            Action.INSERT_AFTER,
            Action.DELETE_ITEM,
            None,
            Action.PASTE_ITEM_BEFORE,
            Action.PASTE_ITEM_AFTER,
            Action.EDIT_ITEM,
            Action.TOGGLE_COMPLETE,
            Action.TOGGLE_HIDE_COMPLETE,
            None,
            Action.SEARCH,
            Action.SELECT_NEXT_SEARCH_RESULT,
            Action.SELECT_PREVIOUS_SEARCH_RESULT,
            None,
            Action.QUIT
        ]
        self.set_widgets([title] + [self._label_for_action(a) for a in actions])

    def show(self):
        self._manager.add(self)
        self._visible = True

    def handle_key(self, key: str) -> bool:
        if not self._visible:
            return False

        if key == ptg.keys.ESC:
            self._visible = False
            self._manager.remove(self)
            return True

    def _label_for_action(self, action: Action | None) -> ptg.Label:
        if action is None:
            return ptg.Label("")

        key = display_text_for_key(ALL_ACTIONS[action].key)
        help_text = ALL_ACTIONS[action].help_text
        spaces = " " * (7 - len(key))
        return ptg.Label(
            f"[green]{key}[/]{spaces}{help_text}", parent_align=HorizontalAlignment.LEFT
        )
