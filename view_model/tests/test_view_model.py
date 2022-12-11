from pathlib import Path

import pytest

from config import config
from todo_list.todo_list import TodoItem
from todo_list.tree import TreeNode
from view_model.view_model import ViewModel


@pytest.fixture
def tree_str():
    return """
- Item 1
  - [COMPLETE] Item 1.1
  "Subtitle"
    - Item 1.1.1
    - Item 1.1.2
  - Item 1.2
    - [COLLAPSED] Item 1.2.1
      - Item 1.2.1.1
- Item 2"""


@pytest.fixture
def tree_root(tree_str):
    return TreeNode.from_string(tree_str, TodoItem.tree_node_from_str)


@pytest.fixture
def save_file():
    return Path("filename")


@pytest.fixture
def view_model(tree_root, save_file):
    vm = ViewModel(tree_root, save_file, config.ConfigManager())
    vm.set_window_height(10)

    def mock_save():
        pass

    vm.save_to_file = mock_save

    return vm


def test_init(view_model):
    assert len(view_model.tree_root.children) == 2


def test_set_window_height(view_model):
    view_model.set_window_height(3)
    assert view_model._last_item_on_screen == 3


def test_list_items(view_model):
    list_items = view_model.list_items()
    expected_items = [
        "Item 1",
        "Item 1.1",
        "Item 1.1.1",
        "Item 1.1.2",
        "Item 1.2",
        "Item 1.2.1",
        "Item 2",
    ]
    assert len(list_items) == len(expected_items)
    for result, expected in zip(list_items, expected_items):
        assert result.text == expected


def test_list_items_hide_complete(view_model):
    assert not view_model._config_manager.hide_complete_items
    view_model.toggle_hide_complete_items()
    list_items = view_model.list_items()
    expected_items = [
        "Item 1",
        "Item 1.2",
        "Item 1.2.1",
        "Item 2",
    ]
    assert len(list_items) == len(expected_items)
    for result, expected in zip(list_items, expected_items):
        assert result.text == expected

def test_list_title(view_model):
    assert view_model.list_title() == "Toppnivå"
    view_model.set_as_root(view_model.tree_root.first_child())
    assert view_model.list_title() == "Item 1"


def test_select_next(view_model):
    assert view_model.selected_node.data.text == "Item 1"
    view_model.select_next()
    assert view_model.selected_node.data.text == "Item 1.1"


def test_select_previous(view_model):
    assert view_model.selected_node.data.text == "Item 1"
    view_model.select_previous()
    assert view_model.selected_node.data.text == "Item 2"


def test_select_top_bottom_middle(view_model):
    view_model.set_window_height(3)

    view_model.select_bottom()
    assert view_model.selected_node.data.text == "Item 1.1.1"

    view_model.select_top()
    assert view_model.selected_node.data.text == "Item 1"

    view_model.select_middle()
    assert view_model.selected_node.data.text == "Item 1.1"


def test_select_first_node(view_model):
    assert view_model.tree_root.data.text == "root"
    view_model.selected_node = None
    view_model.select_first()
    assert view_model.selected_node.data.text == "Item 1"


def test_set_as_root(view_model):
    view_model.set_as_root(view_model.tree_root.first_child())
    assert view_model.tree_root.data.text == "Item 1"
    assert view_model.selected_node.data.text == "Item 1.1"


def test_set_as_root_when_first_child_is_complete(view_model):
    view_model._config_manager.hide_complete_items = True
    assert view_model.selected_node.data.text == "Item 1"
    view_model.set_as_root(view_model.selected_node)
    assert view_model.selected_node.data.text == "Item 1.2"
    assert not view_model.selected_node.data.complete


def test_move_root_upwards(view_model):
    view_model.set_as_root(view_model.tree_root.first_child())
    assert view_model.tree_root.data.text == "Item 1"
    assert view_model.selected_node.data.text == "Item 1.1"

    view_model.move_root_upwards()
    assert view_model.tree_root.data.text == "root"
    assert view_model.selected_node.data.text == "Item 1"


def test_toggle_collapse_node(view_model):
    assert not view_model.selected_node.data.collapsed

    view_model.toggle_collapse_node()
    assert view_model.selected_node.data.collapsed
    assert not view_model.selected_node.first_child().data.collapsed

    view_model.toggle_collapse_node()
    assert not view_model.selected_node.data.collapsed


def test_insert_start_cancel(view_model):
    assert not view_model.is_inserting

    view_model.start_insert()
    assert view_model.is_inserting

    view_model.cancel_insert()
    assert not view_model.is_inserting


def test_edit_start_cancel(view_model):
    assert not view_model.is_editing

    view_model.start_edit()
    assert view_model.is_editing

    view_model.cancel_edit()
    assert not view_model.is_editing


def test_insert_item(view_model):
    view_model.insert_item("New item")

    assert view_model.tree_root.children[1].data.text == "New item"


def test_edit(view_model):
    assert view_model.selected_node.data.text == "Item 1"

    view_model.start_edit()
    view_model.finish_edit("Edited")

    assert view_model.selected_node.data.text == "Edited"

def test_is_searching(view_model):
    assert not view_model.is_searching
    view_model.update_search("test")
    assert view_model.is_searching
    view_model.cancel_search()
    assert not view_model.is_searching

def test_finish_search(view_model):
    view_model.update_search("Item 2")
    view_model.finish_search()
    assert not view_model.is_searching
    assert view_model.selected_node.data.text == "Item 2"

def test_select_next_and_previous_search_result(view_model):
    view_model.update_search("Item 1.1")
    assert view_model.is_searching
    assert view_model.selected_node.data.text == "Item 1.1"
    view_model.select_next_search_result()
    assert view_model.selected_node.data.text == "Item 1.1.1"
    view_model.select_previous_search_result()
    assert view_model.selected_node.data.text == "Item 1.1"
    view_model.finish_search()
    assert view_model.selected_node.data.text == "Item 1.1"
    assert not view_model.is_searching

def test_toggle_complete(view_model):
    assert not view_model.selected_node.data.complete

    view_model.toggle_complete()

    assert view_model.selected_node.data.complete
    for node in view_model.selected_node.children:
        assert node.data.complete

    view_model.toggle_complete()
    assert not view_model.selected_node.data.complete
    # Children should remain complete
    for node in view_model.selected_node.children:
        assert node.data.complete


def test_index_of_selected_node(view_model):
    assert view_model.index_of_selected_node() == 0
    view_model.select_next()
    assert view_model.index_of_selected_node() == 1


def test_delete_item(view_model):
    assert len(view_model.tree_root.children) == 2
    assert view_model.selected_node.data.text == "Item 1"
    view_model.delete_item()
    assert len(view_model.tree_root.children) == 1
    assert view_model.selected_node.data.text == "Item 2"


def test_paste_item(view_model):
    assert len(view_model.tree_root.children) == 2
    assert view_model.selected_node.data.text == "Item 1"
    view_model.delete_item()
    assert len(view_model.tree_root.children) == 1
    assert view_model.selected_node.data.text == "Item 2"

    view_model.paste_item()
    #assert len(view_model.tree_root.children) == 2
