from __future__ import annotations

from typing import Optional, TypeVar, List, Generator, Callable
import uuid

T = TypeVar("T")
FilterFunction = Callable[["TreeNode"], bool]


class TreeNode:
    def __init__(self, data: T, level: int = 0):
        self.data = data
        self._children: List[TreeNode] = []
        self._parent: Optional[TreeNode] = None
        self._level: int = level
        self._id = uuid.uuid1()

    def prepend_child(self, child: TreeNode):
        self._children.insert(0, child)
        child._level = self._level + 1
        child._parent = self

    def append_child(self, child: TreeNode, after_child: Optional[TreeNode] = None):
        if after_child:
            index = self.children.index(after_child)
            self.children.insert(index + 1, child)
        else:
            self._children.append(child)
        child._level = self._level + 1
        child._parent = self

    def has_children(self) -> bool:
        return len(self.children) > 0

    def add_sibling(self, new_node: TreeNode):
        self.parent.append_child(new_node, after_child=self)

    def remove_node(self, node: TreeNode):
        if node in self._children:
            self._children.remove(node)
            return
        for child in self.children:
            child.remove_node(node)

    def first_child(
        self, filter_func: Optional[FilterFunction] = None
    ) -> Optional[TreeNode]:
        try:
            if filter_func:
                return [child for child in self.children if filter_func(child)][0]
            else:
                return self.children[0]
        except IndexError:
            return None

    def last_child(
        self, filter_func: Optional[FilterFunction] = None
    ) -> Optional[TreeNode]:
        try:
            if filter_func:
                return [child for child in self.children if filter_func(child)][-1]
            else:
                return self.children[-1]
        except IndexError:
            return None

    def node_after(
        self, node: TreeNode, filter_func: Optional[FilterFunction] = None
    ) -> TreeNode:
        if not self.has_children():
            return self

        if filter_func:
            generator = self.gen_all_nodes_with_condition(filter_func)
        else:
            generator = self.gen_all_nodes()
        for item in generator:
            if item == node:
                try:
                    return next(generator)
                except StopIteration:
                    return self.first_child(filter_func)
        # Did not find the given node in the sub-tree
        return self

    def node_before(
        self, node: TreeNode, filter_func: Optional[FilterFunction] = None
    ) -> TreeNode:
        if not self.has_children():
            return self

        # TODO: this could be optimized
        if filter_func:
            all_items = list(self.gen_all_nodes_with_condition(filter_func))
        else:
            all_items = list(self.gen_all_nodes())
        generator = reversed(all_items)
        for item in generator:
            if item == node:
                try:
                    return next(generator)
                except StopIteration:
                    return all_items[-1]
        # Did not find the given node in the sub-tree
        return self

    def change_level(self, delta: int):
        self._level += delta
        for child in self.children:
            child.change_level(delta)

    def gen_all_nodes(self) -> Generator[TreeNode]:
        for child in self.children:
            yield child
            for node in child.gen_all_nodes():
                yield node

    def gen_all_nodes_with_condition(
        self, filter_function: FilterFunction
    ) -> Generator[TreeNode]:
        for child in self.children:
            if not filter_function(child):
                continue
            yield child
            for node in child.gen_all_nodes_with_condition(filter_function):
                yield node

    def node_at_index(self, index: int) -> Optional[TreeNode]:
        for i, node_i in enumerate(self.gen_all_nodes()):
            if i == index:
                return node_i
        return None

    def index_for_node(self, node: TreeNode) -> int:
        for i, node_i in enumerate(self.gen_all_nodes()):
            if node_i == node:
                return i
        raise ValueError(
            "Can not find index for node, because node does not exist in this tree."
        )

    @property
    def parent(self) -> TreeNode:
        return self._parent

    @property
    def level(self):
        return self._level

    def set_level(self, new_level: int):
        self._level = new_level

    def apply_to_self_and_children(self, callable: Callable[[TreeNode], None]):
        callable(self)
        for child in self.children:
            child.apply_to_self_and_children(callable)

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

    def is_equivalent_to(self, other) -> bool:
        data_equal = self.data == other.data
        level_equal = self._level == other._level
        if (not data_equal) or (not level_equal):
            return False
        for child, other_child in zip(self.children, other.children):
            if not child.is_equivalent_to(other_child):
                return False
        return True

    @classmethod
    def from_string(
        cls, s: str, node_from_str: Callable[[str, TreeNode], Optional[TreeNode]]
    ) -> TreeNode:
        current_level = 0
        insert_point = node_from_str("- root", None)  # TODO
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
                insert_point.append_child(node)
            except ValueError as e:
                continue

        root = insert_point.root()
        root.change_level(-1)
        return root
