from copy import deepcopy
from pathlib import Path

import pytest

from listigt.config import config
from listigt.todo_list import todo_list
from listigt.todo_list.tree import TreeNode
from listigt.view_model.view_model import ViewModel
from listigt.utils.optional import Optional


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
    return TreeNode.from_string(tree_str, todo_list.TodoItem.tree_node_from_str)


@pytest.fixture
def save_file():
    return Path("filename")


@pytest.fixture
def view_model(tree_root, save_file):
    config_manager = config.ConfigManager()
    config_manager.hide_complete_items = False
    config_manager.root_node_index = Optional.none()

    vm = ViewModel(tree_root, config_manager)
    vm.set_window_size(50, 10)

    def mock_save():
        pass

    vm.save_to_file = mock_save

    return vm


def test_init(view_model):
    assert len(view_model.tree_root.children) == 2


def test_set_window_height(view_model):
    view_model.set_window_size(0, 3)
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
    assert view_model.list_title() == ("Toppnivå", "")
    view_model.set_as_root(view_model.tree_root.first_child())
    assert view_model.list_title() == ("Item 1", "")
    view_model.set_as_root(view_model.tree_root.first_child())
    assert view_model.list_title() == ("Item 1.1", "Item 1 > ")


def test_select_next(view_model):
    assert view_model.selected_node.value().data.text == "Item 1"
    view_model.select_next()
    assert view_model.selected_node.value().data.text == "Item 1.1"


def test_select_previous(view_model):
    assert view_model.selected_node.value().data.text == "Item 1"
    view_model.select_previous()
    assert view_model.selected_node.value().data.text == "Item 2"


def test_select_top_bottom_middle(view_model):
    view_model.set_window_size(0, 3)

    view_model.select_bottom()
    assert view_model.selected_node.value().data.text == "Item 1.1.1"

    view_model.select_top()
    assert view_model.selected_node.value().data.text == "Item 1"

    view_model.select_middle()
    assert view_model.selected_node.value().data.text == "Item 1.1"


def test_select_first_node(view_model):
    assert view_model.tree_root.data.text == "root"
    view_model.selected_node = Optional.none()
    view_model.select_first()
    assert view_model.selected_node.value().data.text == "Item 1"


def test_set_as_root(view_model):
    view_model.set_as_root(view_model.tree_root.first_child())
    assert view_model.tree_root.data.text == "Item 1"
    assert view_model.selected_node.value().data.text == "Item 1.1"


def test_set_as_root_when_first_child_is_complete(view_model):
    view_model.toggle_hide_complete_items()
    assert view_model.selected_node.value().data.text == "Item 1"
    view_model.set_as_root(view_model.selected_node)
    assert view_model.selected_node.value().data.text == "Item 1.2"
    assert not view_model.selected_node.value().data.complete


def test_move_root_upwards(view_model):
    view_model.set_as_root(view_model.tree_root.first_child())
    assert view_model.tree_root.data.text == "Item 1"
    assert view_model.selected_node.value().data.text == "Item 1.1"

    view_model.move_root_upwards()
    assert view_model.tree_root.data.text == "root"
    assert view_model.selected_node.value().data.text == "Item 1"


def test_toggle_collapse_node(view_model):
    assert not view_model.selected_node.value().data.collapsed

    view_model.toggle_collapse_node()
    assert view_model.selected_node.value().data.collapsed
    assert not view_model.selected_node.value().first_child().value().data.collapsed

    view_model.toggle_collapse_node()
    assert not view_model.selected_node.value().data.collapsed


def test_insert_start_cancel(view_model):
    assert not view_model.is_inserting

    view_model.start_insert_after()
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
    # Node has children, so new item should also be a child
    view_model.set_as_root(view_model.tree_root.first_child())
    assert view_model.selected_node.value().data.text == "Item 1.1"
    view_model.insert_item("New item")
    assert view_model.selected_node.value().data.text == "New item"
    assert view_model.selected_node.value().parent.value().data.text == "Item 1.1"

    # Node has no children, so new item should be a sibling
    view_model.set_as_root(view_model.selected_node.value().first_child())
    assert view_model.selected_node.value().data.text == "New item"
    view_model.insert_item("New item 2")
    assert view_model.selected_node.value().data.text == "New item 2"
    assert view_model.selected_node.value().parent.value().data.text == "Item 1.1"

    assert not view_model.is_inserting


def test_edit(view_model):
    assert view_model.selected_node.value().data.text == "Item 1"

    view_model.start_edit()
    view_model.finish_edit("Edited")

    assert view_model.selected_node.value().data.text == "Edited"

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
    assert view_model.selected_node.value().data.text == "Item 2"

def test_select_next_and_previous_search_result(view_model):
    view_model.update_search("Item 1.1")
    assert view_model.is_searching
    assert view_model.selected_node.value().data.text == "Item 1.1"
    view_model.select_next_search_result()
    assert view_model.selected_node.value().data.text == "Item 1.1.1"
    view_model.select_previous_search_result()
    assert view_model.selected_node.value().data.text == "Item 1.1"
    view_model.finish_search()
    assert view_model.selected_node.value().data.text == "Item 1.1"
    assert not view_model.is_searching

def test_toggle_complete(view_model):
    assert not view_model.selected_node.value().data.complete

    view_model.toggle_complete()

    assert view_model.selected_node.value().data.complete
    for node in view_model.selected_node.value().children:
        assert node.data.complete

    view_model.toggle_complete()
    assert not view_model.selected_node.value().data.complete
    # Children should remain complete
    for node in view_model.selected_node.value().children:
        assert node.data.complete


def test_index_of_selected_node(view_model):
    assert view_model.index_of_selected_node() == 0
    view_model.select_next()
    assert view_model.index_of_selected_node() == 1


def test_delete_item(view_model):
    assert len(view_model.tree_root.children) == 2
    assert view_model.selected_node.value().data.text == "Item 1"
    view_model.delete_item()
    assert len(view_model.tree_root.children) == 1
    assert view_model.selected_node.value().data.text == "Item 2"


def test_paste_item(view_model):
    item1 = view_model.selected_node.value()
    assert item1.data.text == "Item 1"
    view_model.select_next()
    assert view_model.selected_node.value().data.text == "Item 1.1"
    pasted_node = view_model.selected_node.value()
    view_model.delete_item()
    assert view_model.selected_node.value().data.text == "Item 1.2"

    view_model.selected_node = view_model.tree_root.first_child().value().first_child().value().first_child() # TODO: method chaining
    item1_2 = view_model.selected_node.value().parent.value()
    assert item1_2.data.text == "Item 1.2"
    assert view_model.selected_node.value().data.text == "Item 1.2.1"
    view_model.paste_item()

    assert pasted_node.data.text == "Item 1.1"
    assert pasted_node.parent.value() == item1_2
    assert pasted_node.level == item1_2.level + 1
    for child in pasted_node.children:
        assert child.level == pasted_node.level + 1


def test_undo(view_model):
    original_tree = deepcopy(view_model.tree_root.root())
    assert original_tree.is_equivalent_to(view_model.tree_root.root())

    view_model.select_next()
    view_model.insert_item("Test")
    assert not original_tree.is_equivalent_to(view_model.tree_root.root())
    view_model.undo()
    assert original_tree.is_equivalent_to(view_model.tree_root.root())

    view_model.select_first()
    view_model.select_next()
    view_model.select_next()
    view_model.delete_item()
    assert not original_tree.is_equivalent_to(view_model.tree_root.root())
    view_model.undo()
    assert original_tree.is_equivalent_to(view_model.tree_root.root())

    view_model.undo()
    assert original_tree.is_equivalent_to(view_model.tree_root.root())
