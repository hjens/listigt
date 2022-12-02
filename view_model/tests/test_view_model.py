from pathlib import Path

import pytest

from todo_list.todo_list import TodoItem
from todo_list.tree import TreeNode
from view_model.view_model import ViewModel


@pytest.fixture
def tree_str():
    return """
- Item 1
  - Item 1.1
  "Subtitle"
    - [COMPLETE] Item 1.1.1
    - Item 1.1.2
  - Item 1.2
    - Item 1.2.1
      - [COMPLETE] [COLLAPSED] Item 1.2.1.1
- Item 2"""


@pytest.fixture
def tree_root(tree_str):
    return TreeNode.from_string(tree_str, TodoItem.tree_node_from_str)


@pytest.fixture
def save_file():
    return Path("filename")


@pytest.fixture
def view_model(tree_root, save_file):
    return ViewModel(tree_root, save_file)


def test_init(view_model):
    assert len(view_model.tree_root.children) == 2
