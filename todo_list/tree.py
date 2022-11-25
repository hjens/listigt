from __future__ import annotations

from typing import Optional, TypeVar, List, Generator
import uuid

T = TypeVar("T")


class TreeNode:
    def __init__(self, data: T, level: int = 0):
        self.data = data
        self._children: List[TreeNode] = []
        self._parent: Optional[TreeNode] = None
        self._level: int = level
        self._id = uuid.uuid1()

    def add_child(self, child: TreeNode):
        self._children.append(child)
        child._level = self._level + 1
        child._parent = self

    def first_child(self) -> TreeNode:
        return self.children[0]

    def last_child(self) -> TreeNode:
        return self.children[-1]

    def change_level(self, delta: int):
        self._level += delta
        for child in self.children:
            child.change_level(delta)

    def gen_all_nodes(self) -> Generator[TreeNode]:
        yield self
        for child in self.children:
            for node in child.gen_all_nodes():
                yield node

    @property
    def parent(self) -> TreeNode:
        return self._parent

    @property
    def level(self):
        return self._level

    def set_level(self, new_level: int):
        self._level = new_level

    @property
    def children(self) -> List[TreeNode]:
        return self._children

    def root(self) -> TreeNode:
        out = self
        while True:
            if out.parent is None:
                return out
            out = out.parent

    def __str__(self) -> str:
        indent = " " * self._level * 2
        s = indent + f"- {self.data}"
        for child in self.children:
            s += indent + f"\n{child}"
        return s

    def __eq__(self, other) -> bool:
        return self._id == other._id

    def equivalent(self, other) -> bool:
        data_equal = self.data == other.data
        level_equal = self._level == other._level
        if (not data_equal) or (not level_equal):
            return False
        for child, other_child in zip(self.children, other.children):
            if not child.equivalent(other_child):
                return False
        return True
