from copy import deepcopy

import pytest

from todo_list.todo_list import TodoItem
from todo_list.tree import TreeNode


@pytest.mark.parametrize(
    "input, expected",
    [
        ("- Text", TreeNode(TodoItem("Text"), level=0)),
        ("  - Text", TreeNode(TodoItem("Text"), level=1)),
        ("    - [COMPLETE] Text", TreeNode(TodoItem("Text", complete=True), level=2)),
    ],
)
def test_tree_node_from_str(input, expected):
    result = TodoItem.tree_node_from_str(input, last_node=None)
    assert result.is_equivalent_to(expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (TreeNode(TodoItem("Text"), level=0), "- Text"),
        (TreeNode(TodoItem("Text"), level=1), "  - Text"),
        (TreeNode(TodoItem("Text", complete=True), level=1), "  - [COMPLETE] Text"),
    ],
)
def test_tree_node_to_str(input, expected):
    result = str(input)
    assert result == expected


def test_tree_to_and_from_str():
    root = TreeNode(TodoItem("root"))
    leaf1 = TreeNode(TodoItem("leaf1"))
    leaf2 = TreeNode(TodoItem("leaf2"))
    root.append_child(leaf1)
    root.append_child(leaf2)

    tree_as_str = str(root)

    tree_from_str = TreeNode.from_string(tree_as_str, TodoItem.tree_node_from_str)

    assert tree_from_str.first_child().is_equivalent_to(root)


def test_build_tree_with_subtitle():
    s = """- Item 1
  - Item 1.1
  "Subtitle"
    - [COMPLETE] Item 1.1.1
    - Item 1.1.2
  - Item 1.2
    - Item 1.2.1
      - [COMPLETE] [COLLAPSED] Item 1.2.1.1
- Item 2"""
    root = TreeNode.from_string(s, TodoItem.tree_node_from_str)
    assert len(root.children) == 2
    assert root.children[0].children[0].data.text == "Item 1.1"
    assert root.children[0].children[0].data.subtitle == "Subtitle"
    assert root.first_child().first_child().first_child().data.text == "Item 1.1.1"
    assert root.first_child().first_child().first_child().data.complete
    assert not root.first_child().first_child().first_child().data.collapsed
    node = root.first_child().children[1].children[0].children[0]
    assert node.data.text == "Item 1.2.1.1"
    assert node.data.complete
    assert node.data.collapsed


def test_copy():
    node = TreeNode(TodoItem("test"))
    deep_copied_node = deepcopy(node)
    deep_copied_node.data.text = "changed"

    assert node.data.text == "test"
    assert deep_copied_node.data.text == "changed"
