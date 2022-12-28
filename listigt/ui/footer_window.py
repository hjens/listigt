import pytermgui as ptg

from listigt.view_model.view_model import ViewModel
from listigt.ui.search_field import SearchInput
from listigt.ui.action import ALL_ACTIONS, Action


class FooterWindow(ptg.Window):
    def __init__(self, view_model: ViewModel, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self._view_model = view_model

        self._help_label = ptg.Label("Press ? to show help")
        self._search_input = SearchInput(self._view_model)
        self.set_widgets([ptg.Splitter(self._search_input, self._help_label)])

    def handle_key(self, key: str) -> bool:
        if self._view_model.is_searching:
            if self._search_input.handle_key(key):
                return True

        search_key = ALL_ACTIONS[Action.SEARCH].key
        if key == search_key and (not self._view_model.is_searching):
            self._search_input.select(0)
            self._view_model.update_search("")
            self._search_input.prompt = "Search: "
            return True

        return False
