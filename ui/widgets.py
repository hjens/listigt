from typing import Any, List

import pytermgui as ptg

from view_model import view_model


class TodoItemTree(ptg.Container):
    def __init__(self, vm: view_model.ViewModel, **attrs: Any):
        super().__init__(**attrs)
        self._view_model = vm
        self._update_widgets()

    def _update_widgets(self):
        labels = [ptg.Label(item) for item in self._view_model.item_titles()]
        self.set_widgets(labels)
