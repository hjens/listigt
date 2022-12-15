from pathlib import Path
from typing import Optional

import toml


class ConfigManager:
    def __init__(self, save_file: Optional[Path] = None, config_file: Optional[Path] = None):
        self._root_node_index = -1
        self._hide_complete_items = False
        self._save_file_override = save_file
        self._config_file_override = save_file
        self._load_config()

    @property
    def root_node_index(self) -> int:
        return None if self._root_node_index < 0 else self._root_node_index

    @root_node_index.setter
    def root_node_index(self, new_value: Optional[int]):
        self._root_node_index = -1 if new_value is None else new_value

    @property
    def hide_complete_items(self) -> bool:
        return self._hide_complete_items

    @hide_complete_items.setter
    def hide_complete_items(self, new_value: bool):
        self._hide_complete_items = new_value

    @property
    def default_config_dir(self) -> Path:
        return Path.home() / ".listigt"

    @property
    def save_file(self) -> Path:
        if self._save_file_override:
            return self._save_file_override

        return self.default_config_dir / "savefile"

    @property
    def config_file(self) -> Path:
        if self._config_file_override:
            return self._config_file_override

        return self.default_config_dir / "config.toml"

    def _load_config(self):
        try:
            toml_data = toml.load(str(self.config_file))
            self._root_node_index = toml_data["State"].get("root_index", None)
            self._hide_complete_items = toml_data["State"].get(
                "hide_complete_items", True
            )
        except FileNotFoundError:
            pass
        except KeyError:
            pass

    def save_config(self):
        self.config_file.parent.mkdir(exist_ok=True)
        
        with open(self.config_file, "w") as f:
            toml.dump(
                {
                    "State": {
                        "root_index": self._root_node_index,
                        "hide_complete_items": self._hide_complete_items,
                    }
                },
                f,
            )
