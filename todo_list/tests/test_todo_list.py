import pytest

from todo_list.todo_list import TodoItem
from todo_list.tree import TreeNode, tree_nodes_from_string


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
    assert result == expected


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


def test_tree_to_str():
    root = TreeNode(TodoItem("root"))
    leaf1 = TreeNode(TodoItem("leaf1"))
    leaf2 = TreeNode(TodoItem("leaf2"))
    root.add_child(leaf1)
    root.add_child(leaf2)

    expected = "- root\n  - leaf1\n  - leaf2"

    result = str(root)

    assert result == expected

def test_to_and_from_str():
    root = TreeNode(TodoItem("root"))
    leaf1 = TreeNode(TodoItem("leaf1"))
    leaf2 = TreeNode(TodoItem("leaf2"))
    root.add_child(leaf1)
    root.add_child(leaf2)

    tree_as_str = str(root)

    tree_from_str = tree_nodes_from_string(tree_as_str, TodoItem.tree_node_from_str)

    assert tree_from_str[0] == root


def test_build_large_tree_with_subtitle():
    s = \
"""- Item 1
  - Item 1.1
  "Subtitle"
    - [COMPLETE] Item 1.1.1
    - Item 1.1.2
  - Item 1.2
    - Item 1.2.1
     - Item 1.2.1.1
- Item 2"""
    tree_nodes = tree_nodes_from_string(s, TodoItem.tree_node_from_str)
    assert len(tree_nodes) == 2
    assert tree_nodes[0].children[0].data.text == "Item 1.1"
    assert tree_nodes[0].children[0].data.subtitle == "Subtitle"
