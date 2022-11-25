from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Callable, Generator

from todo_list.tree import TreeNode


COMPLETE_TEXT = "[COMPLETE]"
SPACES_PER_LEVEL = 2


@dataclass
class TodoItem:
    text: str
    subtitle: str = ""
    complete: bool = False

    def __str__(self):
        complete_str = f"{COMPLETE_TEXT} " if self.complete else ""
        subtitle_str = f'\n"{self.subtitle}"' if self.subtitle else ""
        return f"{complete_str}{self.text}{subtitle_str}"

    @classmethod
    def tree_node_from_str(cls, s: str, last_node: TreeNode) -> Optional[TreeNode]:
        if s.strip().startswith('"') and s.strip().endswith('"'):
            subtitle = s.strip()[1:-1]
            last_node.data.subtitle = subtitle
            return None

        indent, text = s.split("- ")[:2]
        if len(indent) % SPACES_PER_LEVEL != 0:
            raise ValueError(
                f"Found indent that is not a multiple of {SPACES_PER_LEVEL}"
            )
        level = int(len(indent) / SPACES_PER_LEVEL)
        complete = COMPLETE_TEXT in text
        text = text.replace(COMPLETE_TEXT, "").strip()
        return TreeNode(data=TodoItem(text=text, complete=complete), level=level)
