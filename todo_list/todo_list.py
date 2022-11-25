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


class TodoList:
    def __init__(self, items: List[TreeNode]):
        self.items = items

    def add_item_after(self, item: TreeNode, new_item: TreeNode):
        if item.parent is None:
            items = self.items
        else:
            items = item.parent.children
        index = items.index(item)
        new_item.set_level(items[0].level)
        items.insert(index + 1, new_item)

    def remove_item(self, item_to_remove: TreeNode):
        if item_to_remove in self.items:
            self.items.remove(item_to_remove)
            return
        for item in self.items:
            item.remove_node(item_to_remove)

    def gen_all_items(self) -> Generator[TreeNode]:
        for item in self.items:
            for node in item.gen_all_nodes():
                yield node

    def node_after(self, node: TreeNode) -> TreeNode:
        # TODO: this could be optimized
        generator = self.gen_all_items()
        for item in generator:
            if item == node:
                try:
                    return next(generator)
                except StopIteration:
                    return self.items[0]
        assert False, "This should not happen"

    def node_before(self, node: TreeNode) -> TreeNode:
        # TODO: this could be optimized
        all_items = list(self.gen_all_items())
        generator = reversed(all_items)
        for item in generator:
            if item == node:
                try:
                    return next(generator)
                except StopIteration:
                    return all_items[-1]
        assert False, "This should not happen"

    @classmethod
    def from_string(
        cls, s: str, node_from_str: Callable[[str, TreeNode], Optional[TreeNode]]
    ) -> TodoList:
        current_level = 0
        insert_point = TreeNode("root")
        node = insert_point
        for line in s.splitlines():
            try:
                node = node_from_str(line, node)
                if node is None:
                    continue
                if node.level > current_level:
                    insert_point = insert_point.last_child()
                elif node._level < current_level:
                    for _ in range(current_level - node.level):
                        insert_point = insert_point.parent
                current_level = node.level
                insert_point.add_child(node)
            except ValueError as e:
                continue

        insert_point.change_level(-1)
        return TodoList(insert_point.root().children)

    def __str__(self) -> str:
        return "".join([str(n) for n in self.items])
