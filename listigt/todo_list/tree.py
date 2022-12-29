from __future__ import annotations

from typing import TypeVar, List, Generator, Callable
import uuid

from listigt.utils.optional import Optional

T = TypeVar("T")


class TreeNode:
    def __init__(self, data: T, level: int = 0):
        self.data = data
        self.visible = True
        self._children: List[TreeNode] = []
        self._parent: Optional[TreeNode] = Optional.none()
        self._level: int = level
        self._id = uuid.uuid1()

    def prepend_child(self, child: TreeNode):
        self._children.insert(0, child)
        child._level = self._level + 1
        child._parent = Optional.some(self)

    def add_child(
        self,
        child: TreeNode,
        after_child: Optional[TreeNode] = Optional.none(),
        before_child: Optional[TreeNode] = Optional.none(),
    ):
        if after_child.has_value() and before_child.has_value():
            raise ValueError(
                "Only one of after_child and before_child may be specified"
            )

        if after_child := after_child.value_or_none():
            index = self.children.index(after_child)
            self.children.insert(index + 1, child)
        elif before_child := before_child.value_or_none():
            index = self.children.index(before_child)
            self.children.insert(index, child)
        else:
            self._children.append(child)
        child._level = self._level + 1
        child._parent = Optional.some(self)

    def has_children(self) -> bool:
        return len(self.children) > 0

    def add_sibling_after_self(self, new_node: TreeNode):
        self.parent.value().add_child(new_node, after_child=Optional.some(self))

    def add_sibling_before_self(self, new_node: TreeNode):
        self.parent.value().add_child(new_node, before_child=Optional.some(self))

    def remove_node(self, node: TreeNode):
        if node in self._children:
            self._children.remove(node)
            return
        for child in self.children:
            child.remove_node(node)

    def first_child(self, only_visible: bool = False) -> Optional[TreeNode]:
        try:
            if only_visible:
                return Optional.some(
                    [child for child in self.children if child.visible][0]
                )
            else:
                return Optional.some(self.children[0])
        except IndexError:
            return Optional.none()

    def last_child(self, only_visible: bool = False) -> Optional[TreeNode]:
        try:
            if only_visible:
                return Optional.some(
                    [child for child in self.children if child.visible][-1]
                )
            else:
                return Optional.some(self.children[-1])
        except IndexError:
            return Optional.none()

    def node_after(self, node: TreeNode, only_visible: bool = False) -> TreeNode:
        if not self.has_children():
            return self

        if only_visible:
            generator = self.gen_all_visible_nodes()
        else:
            generator = self.gen_all_nodes()
        for item in generator:
            if item == node:
                try:
                    return next(generator)
                except StopIteration:
                    return self.first_child(only_visible=only_visible).value_or(self)
        # Did not find the given node in the sub-tree
        return self

    def node_before(self, node: TreeNode, only_visible: bool = False) -> TreeNode:
        if not self.has_children():
            return self

        # TODO: this could be optimized
        if only_visible:
            all_items = list(self.gen_all_visible_nodes())
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

    def gen_all_visible_nodes(self) -> Generator[TreeNode]:
        for child in self.children:
            if not child.visible:
                continue
            yield child
            for node in child.gen_all_visible_nodes():
                yield node

    def node_at_index(self, index: int) -> Optional[TreeNode]:
        for i, node_i in enumerate(self.gen_all_nodes()):
            if i == index:
                return Optional.some(node_i)
        return Optional.none()

    def index_for_node(self, node: TreeNode) -> Optional[int]:
        for i, node_i in enumerate(self.gen_all_nodes()):
            if node_i == node:
                return Optional.some(i)
        return Optional.none()

    @property
    def parent(self) -> Optional[TreeNode]:
        return self._parent

    @property
    def level(self):
        return self._level

    def set_level(self, new_level: int):
        self._level = new_level

    def update_level_to_parent(self):
        def update_level(node):
            node.set_level(node.parent.value()._level + 1)

        self.apply_to_self_and_children(update_level)

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
            if out.parent.is_none():
                return out
            out = out.parent.value()

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
        num_children_equal = len(self.children) == len(other.children)
        if (not data_equal) or (not level_equal) or (not num_children_equal):
            return False
        for child, other_child in zip(self.children, other.children):
            if not child.is_equivalent_to(other_child):
                return False
        return True

    @classmethod
    def from_string(
        cls,
        s: str,
        node_from_str: Callable[[str, Optional[TreeNode]], Optional[TreeNode]],
    ) -> TreeNode:
        current_level = 0
        insert_point = node_from_str("- root", Optional.none())
        node = insert_point
        for line in s.splitlines():
            try:
                node = node_from_str(line, node)
                if node.is_none():
                    continue
                if node.value().level > current_level:
                    insert_point = insert_point.value().last_child()
                elif node.value().level < current_level:
                    for _ in range(current_level - node.value().level):
                        insert_point = insert_point.value().parent
                current_level = node.value().level
                insert_point.value().add_child(node.value())
            except ValueError as e:
                continue

        root = insert_point.value().root()
        root.change_level(-1)
        return root

    def __repr__(self):
        return f"TreeNode[{str(self.data)}]"
