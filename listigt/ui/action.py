import enum
import pytermgui as ptg

from attr import dataclass

from listigt.utils.optional import Optional


class Action(enum.Enum):
    SELECT_NEXT = enum.auto()
    SELECT_PREVIOUS = enum.auto()
    SELECT_BOTTOM = enum.auto()
    SELECT_TOP = enum.auto()
    SELECT_MIDDLE = enum.auto()
    INSERT_AFTER = enum.auto()
    INSERT_BEFORE = enum.auto()
    DELETE_ITEM = enum.auto()
    SET_AS_ROOT = enum.auto()
    MOVE_ROOT_UP = enum.auto()
    PASTE_ITEM_AFTER = enum.auto()
    PASTE_ITEM_BEFORE = enum.auto()
    EDIT_ITEM = enum.auto()
    TOGGLE_HIDE_COMPLETE = enum.auto()
    UNDO = enum.auto()
    TOGGLE_COMPLETE = enum.auto()
    COLLAPSE = enum.auto()
    SEARCH = enum.auto()
    SELECT_NEXT_SEARCH_RESULT = enum.auto()
    SELECT_PREVIOUS_SEARCH_RESULT = enum.auto()


@dataclass
class KeyboardAction:
    key: str
    help_text: str


ALL_ACTIONS = {
    Action.SELECT_NEXT: KeyboardAction(key="j", help_text="Select next item"),
    Action.SELECT_PREVIOUS: KeyboardAction(key="k", help_text="Select previous item"),
    Action.SELECT_BOTTOM: KeyboardAction(
        key="L", help_text="Select item at bottom of screen"
    ),
    Action.SELECT_TOP: KeyboardAction(
        key="H", help_text="Select item at top of screen"
    ),
    Action.SELECT_MIDDLE: KeyboardAction(
        key="M", help_text="Select item at middle of screen"
    ),
    Action.INSERT_AFTER: KeyboardAction(
        key="n", help_text="Create new item after selection"
    ),
    Action.INSERT_BEFORE: KeyboardAction(
        key="N", help_text="Create new item before selection"
    ),
    Action.DELETE_ITEM: KeyboardAction(key="x", help_text="Cut selected item"),
    Action.SET_AS_ROOT: KeyboardAction(key="l", help_text="Set selected item as top"),
    Action.MOVE_ROOT_UP: KeyboardAction(key="h", help_text="Set item above as top"),
    Action.PASTE_ITEM_AFTER: KeyboardAction(
        key="p", help_text="Paste item after selection"
    ),
    Action.PASTE_ITEM_BEFORE: KeyboardAction(
        key="P", help_text="Paste item before selection"
    ),
    Action.EDIT_ITEM: KeyboardAction(key="e", help_text="Edit item"),
    Action.TOGGLE_HIDE_COMPLETE: KeyboardAction(
        key="c", help_text="Hide/show completed items"
    ),
    Action.UNDO: KeyboardAction(key="u", help_text="Undo"),
    Action.TOGGLE_COMPLETE: KeyboardAction(
        key=ptg.keys.ENTER, help_text="Complete/uncomplete item"
    ),
    Action.COLLAPSE: KeyboardAction(
        key=ptg.keys.SPACE, help_text="Collapse/uncollapse item"
    ),
    Action.SEARCH: KeyboardAction(key="/", help_text="Search"),
}


def action_for_key(key: str) -> Optional[Action]:
    for action, action_details in ALL_ACTIONS.items():
        if action_details.key == key:
            return Optional.some(action)
    return Optional.none()
