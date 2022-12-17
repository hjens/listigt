from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from listigt.todo_list import tree


COMPLETE_TEXT = "[COMPLETE]"
COLLAPSED_TEXT = "[COLLAPSED]"
SPACES_PER_LEVEL = 2


@dataclass
class TodoItem:
    text: str
    subtitle: str = ""
    complete: bool = False
    collapsed: bool = False

    def __str__(self):
        complete_str = f"{COMPLETE_TEXT} " if self.complete else ""
        collapsed_str = f"{COLLAPSED_TEXT} " if self.collapsed else ""
        subtitle_str = f'\n"{self.subtitle}"' if self.subtitle else ""
        return f"{complete_str}{collapsed_str}{self.text}{subtitle_str}"

    @classmethod
    def tree_node_from_str(cls, s: str, last_node: tree.TreeNode) -> Optional[tree.TreeNode]:
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
        collapsed = COLLAPSED_TEXT in text
        text = text.replace(COMPLETE_TEXT, "").strip()
        text = text.replace(COLLAPSED_TEXT, "").strip()
        return tree.TreeNode(
            data=TodoItem(text=text, complete=complete, collapsed=collapsed),
            level=level,
        )