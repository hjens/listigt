import pytest

from todo_list.todo_list import TodoItem
from todo_list.tree import TreeNode, tree_nodes_to_string


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


