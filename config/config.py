from pathlib import Path
from typing import Optional

import toml
from attr import dataclass


CONFIG_FILE = Path("config.toml")



class ConfigManager:
    def __init__(self):
        self._load_config()
        self._selection_index = -1
        self._hide_complete_items = False

    @property
    def selection_index(self) -> Optional[int]:
        return None if self._selection_index < 0 else self._selection_index

    @selection_index.setter
    def selection_index(self, new_value: Optional[int]):
        self._selection_index = -1 if new_value is None else new_value
        self._save_config()

    @property
    def hide_complete_items(self) -> bool:
        return self._hide_complete_items

    @hide_complete_items.setter
    def hide_complete_items(self, new_value: bool):
        self._hide_complete_items = new_value
        self._save_config()

    def _load_config(self):
        try:
            toml_data = toml.load(CONFIG_FILE)
            self._selection_index = toml_data["State"].get(
                "selection_index", None
            )
            self._hide_complete_items = toml_data["State"].get(
                "hide_complete_items", True
            )
        except FileNotFoundError:
            pass
        except KeyError:
            pass

    def _save_config(self):
        with open(CONFIG_FILE, "w") as f:
            toml.dump(
                {
                    "State": {
                        "selection_index": self._selection_index,
                        "hide_complete_items": self._hide_complete_items,
                    }
                },
                f,
            )
