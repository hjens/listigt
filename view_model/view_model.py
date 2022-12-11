import copy
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from config import config
from todo_list.todo_list import TodoItem
from todo_list.tree import TreeNode, FilterFunction


@dataclass
class ListItem:
    text: str
    indentation_level: int
    is_selected: bool
    has_children: bool
    is_completed: bool
    is_collapsed: bool
    is_search_result: bool


@dataclass
class StateBeforeSearch:
    selected_node: Optional[TreeNode]
    collapsed_nodes: List[TreeNode]


class ViewModel:
    def __init__(
        self, tree_root: TreeNode, save_file: Path, config_manager: config.ConfigManager
    ):
        self._config_manager = config_manager
        self._save_file = save_file
        self.tree_root = tree_root
        self.selected_node: Optional[TreeNode] = None
        self._is_inserting = False
        self._cut_item: Optional[TreeNode] = None
        self._item_being_edited: Optional[TreeNode] = None
        self._search_string: Optional[str] = None
        self._search_results: List[TreeNode] = []
        self._state_before_search = StateBeforeSearch(
            selected_node=None, collapsed_nodes=[]
        )
        self._restore_saved_root_node()

        self.set_window_height(0)

        if self.tree_root.children:
            self.selected_node = self.tree_root.first_child(self._make_filter_func())

    def save_to_file(self):
        with open(self._save_file, "w") as f:
            f.write("\n".join([str(item) for item in self.tree_root.root().children]))

    def set_window_height(self, height: int):
        self._num_items_on_screen = height
        self._first_item_on_screen = 0
        self._last_item_on_screen = self._num_items_on_screen

    def _restore_saved_root_node(self):
        root_index = self._config_manager.root_node_index
        root_node = self.tree_root.root().node_at_index(root_index)
        if root_node:
            self.set_as_root(root_node)

    @property
    def num_items_on_screen(self) -> int:
        return self._num_items_on_screen

    def list_items(self) -> List[ListItem]:
        def list_item_from_node(node):
            return ListItem(
                text=node.data.text,
                indentation_level=node.level - self.tree_root.level - 1,
                is_selected=self.selected_node and (node == self.selected_node),
                has_children=node.has_children(),
                is_completed=node.data.complete,
                is_collapsed=node.data.collapsed,
                is_search_result=node in self._search_results,
            )

        items = [list_item_from_node(node) for node in self._all_visible_nodes()]
        self._update_scrolling(len(items))
        return items[self._first_item_on_screen : self._last_item_on_screen]

    def list_title(self) -> str:
        if self.tree_root == self.tree_root.root():
            return "Toppnivå"
        return self.tree_root.data.text

    def toggle_hide_complete_items(self):
        self._config_manager.hide_complete_items = (
            not self._config_manager.hide_complete_items
        )
        self._last_item_on_screen = (
            self._first_item_on_screen + self._num_items_on_screen
        )
        if (
            self.selected_node
            and self._config_manager.hide_complete_items
            and self.selected_node.data.complete
        ):
            # Need to temporarily set the selected node to incomplete, or select_next will not work
            old_selected_node = self.selected_node
            self.selected_node.data.complete = False
            self.select_next()
            old_selected_node.data.complete = True

    def select_next(self):
        if not self.selected_node:
            self.selected_node = self.tree_root.first_child(self._make_filter_func())
        else:
            self.selected_node = self.tree_root.node_after(
                self.selected_node, self._make_filter_func()
            )

    def select_previous(self):
        if not self.selected_node:
            self.selected_node = self.tree_root.first_child(self._make_filter_func())
        else:
            self.selected_node = self.tree_root.node_before(
                self.selected_node, self._make_filter_func()
            )

    def select_bottom(self):
        nodes_list = list(self._all_visible_nodes())
        if len(nodes_list) >= self._last_item_on_screen - 1:
            self.selected_node = nodes_list[self._last_item_on_screen - 1]

    def select_top(self):
        nodes_list = list(self._all_visible_nodes())
        if len(nodes_list) >= self._first_item_on_screen:
            self.selected_node = nodes_list[self._first_item_on_screen]

    def select_middle(self):
        nodes_list = list(self._all_visible_nodes())
        middle_index = (self._first_item_on_screen + self._last_item_on_screen) // 2
        if len(nodes_list) >= middle_index:
            self.selected_node = nodes_list[middle_index]

    def select_first(self):
        self.selected_node = self.tree_root.first_child(self._make_filter_func())

    def set_as_root(self, node: Optional[TreeNode]):
        if node is None:
            return

        self.tree_root = node
        self.tree_root.data.collapsed = False
        if self.tree_root.has_children():
            self.selected_node = self.tree_root.first_child(self._make_filter_func())
        else:
            self.selected_node = None
        self._config_manager.root_node_index = self.tree_root.root().index_for_node(
            self.tree_root
        )

    def move_root_upwards(self):
        if self.tree_root.parent:
            self.selected_node = self.tree_root
            self.tree_root = self.tree_root.parent
            self._first_item_on_screen = self.index_of_selected_node()
            self._last_item_on_screen = (
                self._first_item_on_screen + self._num_items_on_screen
            )
            try:
                self._config_manager.root_node_index = (
                    self.tree_root.root().index_for_node(self.tree_root)
                )
            except ValueError:
                pass

    def toggle_collapse_node(self):
        if self.selected_node:
            self.selected_node.data.collapsed = not self.selected_node.data.collapsed
        self._last_item_on_screen = (
            self._first_item_on_screen + self._num_items_on_screen
        )

    def start_insert(self):
        self._is_inserting = True

    def cancel_insert(self):
        self._is_inserting = False

    @property
    def is_inserting(self):
        return self._is_inserting

    def insert_item(self, item_text: str):
        new_node = TreeNode(data=TodoItem(item_text))
        if self.selected_node:
            self.selected_node.add_sibling(new_node)
        else:
            self.tree_root.add_child(new_node)
        self._is_inserting = False
        self.selected_node = new_node
        self._last_item_on_screen += 1

    def start_edit(self):
        if self.selected_node:
            self._item_being_edited = copy.deepcopy(self.selected_node)

    def cancel_edit(self):
        self._item_being_edited = None

    def finish_edit(self, new_text: str):
        assert self.is_editing
        self.selected_node.data.text = new_text
        self._item_being_edited = None

    @property
    def is_editing(self):
        return self._item_being_edited is not None

    @property
    def is_searching(self):
        return self._search_string is not None

    def update_search(self, search_string: str):
        if search_string == "" and self._state_before_search.selected_node is None:
            self._state_before_search.selected_node = self.selected_node

        self._search_string = search_string
        self._update_search_results()
        if self._search_results:
            self.selected_node = self._search_results[0]

    def cancel_search(self):
        self._search_string = None
        self._search_results = []
        self._restore_search_state()

    def finish_search(self):
        self._search_string = None
        self._search_results = []

    def select_next_search_result(self):
        for i, search_result in enumerate(self._search_results):
            if search_result == self.selected_node:
                self.selected_node = self._search_results[
                    (i + 1) % len(self._search_results)
                ]
                break

    def select_previous_search_result(self):
        for i, search_result in enumerate(self._search_results):
            if search_result == self.selected_node:
                self.selected_node = self._search_results[
                    (i - 1) % len(self._search_results)
                ]
                break

    def _is_search_result(self, node: TreeNode) -> bool:
        if not self.is_searching:
            return False
        return self._search_string.lower() in node.data.text.lower()

    def _update_search_results(self):
        if len(self._search_string) < 3:
            self._search_results = []
            return

        def uncollapse_parents(node):
            if node.parent.data.collapsed:
                node.parent.data.collapsed = False
                self._state_before_search.collapsed_nodes.append(node.parent)
                uncollapse_parents(node.parent)

        search_results = filter(self._is_search_result, self.tree_root.gen_all_nodes())
        self._search_results = list(search_results)
        for result in self._search_results:
            uncollapse_parents(result)

    def _restore_search_state(self):
        self.selected_node = self._state_before_search.selected_node
        for node in self._state_before_search.collapsed_nodes:
            node.data.collapsed = True
        self._state_before_search = StateBeforeSearch(
            selected_node=None, collapsed_nodes=[]
        )

    def toggle_complete(self):
        if self.selected_node is None:
            return

        # Need to move selection before completing, or select_previous will not work
        node_to_complete = self.selected_node
        if self._config_manager.hide_complete_items:
            self.select_previous()

        if not node_to_complete.data.complete:

            def set_complete(node):
                node.data.complete = True

            node_to_complete.apply_to_self_and_children(set_complete)
        else:
            node_to_complete.data.complete = False

    def index_of_selected_node(self) -> int:
        for index, item in enumerate(self._all_visible_nodes()):
            if self.selected_node and (item == self.selected_node):
                return index
        return 0

    def delete_item(self):
        if node_to_remove := self.selected_node:
            self._cut_item = node_to_remove
            self.select_next()
            self.tree_root.remove_node(node_to_remove)
            if not self.tree_root.has_children():
                self.selected_node = None

    def paste_item(self):
        if self._cut_item is None:
            return

        if self.selected_node:
            self.selected_node.add_sibling(self._cut_item)
        else:
            self.tree_root.add_child(self._cut_item)
        self._cut_item = None

    def _update_scrolling(self, num_lines: int):
        if num_lines <= self._num_items_on_screen:
            self._first_item_on_screen = 0
            self._last_item_on_screen = num_lines

        selection_index = self.index_of_selected_node()
        if selection_index < self._first_item_on_screen:
            self._first_item_on_screen = selection_index
            self._last_item_on_screen = min(
                self._first_item_on_screen + self._num_items_on_screen, num_lines
            )
        elif selection_index >= self._last_item_on_screen:
            self._last_item_on_screen = selection_index + 1
            self._first_item_on_screen = max(
                0, self._last_item_on_screen - self._num_items_on_screen
            )

    def _all_visible_nodes(self):
        return self.tree_root.gen_all_nodes_with_condition(self._make_filter_func())

    def _make_filter_func(self) -> FilterFunction:
        def filter_func(node: TreeNode) -> bool:
            # Always hide completed items if hide_complete is set
            if self._config_manager.hide_complete_items and node.data.complete:
                return False
            # Hide children of collapsed nodes
            if node.parent and node.parent.data.collapsed:
                return False
            # Make sure we hide all children of hidden nodes
            if node.parent and not filter_func(node.parent):
                return False
            return True

        return filter_func
