import pytest

from todo_list.todo_list import TodoItem, TodoList
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

    list_from_str = TodoList.from_string(tree_as_str, TodoItem.tree_node_from_str)

    assert list_from_str.items[0] == root


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
    list = TodoList.from_string(s, TodoItem.tree_node_from_str)
    assert len(list.items) == 2
    assert list.items[0].children[0].data.text == "Item 1.1"
    assert list.items[0].children[0].data.subtitle == "Subtitle"


def test_next_item():
    root1 = TreeNode(TodoItem("root1"))
    root2 = TreeNode(TodoItem("root1"))
    leaf1 = TreeNode(TodoItem("leaf1"))
    leaf2 = TreeNode(TodoItem("leaf2"))
    root1.add_child(leaf1)
    root2.add_child(leaf2)

    list_from_items = TodoList([root1, root2])

    assert list_from_items.next_item(root1) == leaf1
    assert list_from_items.next_item(leaf1) == root2
    assert list_from_items.next_item(root2) == leaf2
    assert list_from_items.next_item(leaf2) == root1

def test_previous_item():
    root1 = TreeNode(TodoItem("root1"))
    root2 = TreeNode(TodoItem("root1"))
    leaf1 = TreeNode(TodoItem("leaf1"))
    leaf2 = TreeNode(TodoItem("leaf2"))
    root1.add_child(leaf1)
    root2.add_child(leaf2)

    list_from_items = TodoList([root1, root2])

    assert list_from_items.previous_item(root2) == leaf1
    assert list_from_items.previous_item(leaf1) == root1
    assert list_from_items.previous_item(leaf2) == root2
    assert list_from_items.previous_item(root1) == leaf2
