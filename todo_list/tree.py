from __future__ import annotations

from typing import Optional, TypeVar, List, Callable


T = TypeVar("T")


class TreeNode:
    def __init__(self, data: T, level: int = 0):
        self.data = data
        self._children: List[TreeNode] = []
        self._parent: Optional[TreeNode] = None
        self._level: int = level

    def add_child(self, child: TreeNode):
        self._children.append(child)
        child._level = self._level + 1
        child._parent = self

    def last_child(self) -> TreeNode:
        return self.children[-1]

    def change_level(self, delta: int):
        self._level += delta
        for child in self.children:
            child.change_level(delta)

    @property
    def parent(self) -> TreeNode:
        return self._parent

    @property
    def level(self):
        return self._level

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
        data_equal = self.data == other.data
        level_equal = self._level == other._level
        if (not data_equal) or (not level_equal):
            return False
        for child, other_child in zip(self.children, other.children):
            if not child == other_child:
                return False
        return True


def tree_nodes_from_string(
    s: str, node_from_str: Callable[[str, TreeNode], Optional[TreeNode]]
) -> List[TreeNode]:
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
    return insert_point.root().children


def tree_nodes_to_string(nodes: List[TreeNode]) -> str:
    return "".join([str(n) for n in nodes])
