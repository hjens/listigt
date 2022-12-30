import copy
import enum
from dataclasses import dataclass
from typing import List, Tuple

from listigt.config import config
from listigt.utils.optional import Optional
from listigt.todo_list.todo_list import TodoItem
from listigt.todo_list.tree import TreeNode


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


class InsertionState(enum.Enum):
    NOT_INSERTING = enum.auto()
    BEFORE = enum.auto()
    AFTER = enum.auto()


class ViewModel:
    def __init__(self, tree_root: TreeNode, config_manager: config.ConfigManager):
        self._config_manager = config_manager
        self.tree_root = tree_root
        self.selected_node: Optional[TreeNode] = Optional.none()
        self._insertion_state = InsertionState.NOT_INSERTING
        self._cut_item: Optional[TreeNode] = Optional.none()
        self._item_being_edited: Optional[TreeNode] = Optional.none()
        self._search_string: Optional[str] = Optional.none()
        self._search_results: List[TreeNode] = []
        self._state_before_search = StateBeforeSearch(
            selected_node=Optional.none(), collapsed_nodes=[]
        )
        self._restore_saved_root_node()

        self.set_window_size(0, 0)

        if self.tree_root.children:
            self.selected_node = self.tree_root.first_child(only_visible=True)

        self._undo_stack: List[TreeNode] = []

        self._update_node_visibility()

    def save_to_file(self):
        with open(self._config_manager.save_file, "w") as f:
            f.write("\n".join([str(item) for item in self.tree_root.root().children]))

    def set_window_size(self, width: int, height: int):
        self._width = width
        self._num_items_on_screen = height
        self._first_item_on_screen = 0
        self._last_item_on_screen = self._num_items_on_screen

    def _restore_saved_root_node(self):
        root_index = self._config_manager.root_node_index
        root_node = self.tree_root.root().node_at_index(root_index.value_or(-1))
        if root_node.has_value():
            self.set_as_root(root_node)

    @property
    def num_items_on_screen(self) -> int:
        return self._num_items_on_screen

    def list_items(self) -> List[ListItem]:
        def list_item_from_node(node):
            indent = node.level - self.tree_root.level - 1
            is_selected = (
                self.selected_node.has_value() and node == self.selected_node.value()
            )
            return ListItem(
                text=self._label_display_text(node.data.text, indent, is_selected),
                indentation_level=indent,
                is_selected=is_selected,
                has_children=node.has_children(),
                is_completed=node.data.complete,
                is_collapsed=node.data.collapsed,
                is_search_result=node in self._search_results,
            )

        items = [list_item_from_node(node) for node in self._all_visible_nodes()]
        self._update_scrolling(len(items))
        return items[self._first_item_on_screen : self._last_item_on_screen]

    def list_title(self) -> Tuple[str, str]:
        top_level = self.tree_root.root()
        breadcrumbs = ""
        if self.tree_root == top_level:
            return "Toppnivå", breadcrumbs
        node = self.tree_root
        list_title = node.data.text
        while True:
            node = node.parent.value()
            if node != top_level:
                breadcrumbs = node.data.text + " > " + breadcrumbs
            else:
                break
        return list_title, breadcrumbs

    def toggle_hide_complete_items(self):
        self._config_manager.hide_complete_items = (
            not self._config_manager.hide_complete_items
        )
        self._last_item_on_screen = (
            self._first_item_on_screen + self._num_items_on_screen
        )
        if (
            self.selected_node.has_value()
            and self._config_manager.hide_complete_items
            and self.selected_node.value().data.complete
        ):
            # Need to temporarily set the selected node to incomplete, or select_next will not work
            old_selected_node = self.selected_node
            self.selected_node.value().data.complete = False
            self.select_next()
            old_selected_node.value().data.complete = True

        self._update_node_visibility()

    def select_next(self):
        if self.selected_node.is_none():
            self.selected_node = self.tree_root.first_child(only_visible=True)
        else:
            self.selected_node = Optional.some(
                self.tree_root.node_after(self.selected_node.value(), only_visible=True)
            )

    def select_previous(self):
        if self.selected_node.is_none():
            self.selected_node = self.tree_root.first_child(only_visible=True)
        else:
            self.selected_node = Optional.some(
                self.tree_root.node_before(
                    self.selected_node.value(), only_visible=True
                )
            )

    def select_bottom(self):
        nodes_list = list(self._all_visible_nodes())
        if len(nodes_list) >= self._last_item_on_screen - 1:
            self.selected_node = Optional.some(
                nodes_list[self._last_item_on_screen - 1]
            )

    def select_top(self):
        nodes_list = list(self._all_visible_nodes())
        if len(nodes_list) >= self._first_item_on_screen:
            self.selected_node = Optional.some(nodes_list[self._first_item_on_screen])

    def select_middle(self):
        nodes_list = list(self._all_visible_nodes())
        middle_index = (self._first_item_on_screen + self._last_item_on_screen) // 2
        if len(nodes_list) >= middle_index:
            self.selected_node = Optional.some(nodes_list[middle_index])

    def select_first(self):
        self.selected_node = self.tree_root.first_child(only_visible=True)

    def set_as_root(self, node: Optional[TreeNode]):
        if node.is_none():
            return

        # TODO: handle missing tree_root value properly
        self.tree_root = node.value()
        self.tree_root.data.collapsed = False
        self._config_manager.root_node_index = self.tree_root.root().index_for_node(
            self.tree_root
        )
        self._update_node_visibility()
        self.selected_node = self.tree_root.first_child(only_visible=True)

    def move_root_upwards(self):
        if self.tree_root.parent.has_value():
            self.selected_node = Optional.some(self.tree_root)
            self.tree_root = self.tree_root.parent.value()
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
        if self.selected_node.has_value():
            self.selected_node.value().data.collapsed = (
                not self.selected_node.value().data.collapsed
            )
        self._last_item_on_screen = (
            self._first_item_on_screen + self._num_items_on_screen
        )

        self._update_node_visibility()

    def start_insert_before(self):
        self._insertion_state = InsertionState.BEFORE

    def start_insert_after(self):
        self._insertion_state = InsertionState.AFTER

    def cancel_insert(self):
        self._insertion_state = InsertionState.NOT_INSERTING

    def insertion_index(self) -> int:
        if self.selected_node.has_value():
            if self._insertion_state == InsertionState.AFTER:
                return self.index_of_selected_node() + 2
            elif self._insertion_state == InsertionState.BEFORE:
                return self.index_of_selected_node() + 1
        else:
            return 1

    @property
    def is_inserting(self):
        return self._insertion_state is not InsertionState.NOT_INSERTING

    def insert_item(self, item_text: str):
        self._push_undo_state()
        new_node = TreeNode(data=TodoItem(item_text))
        if selected_node := self.selected_node.value_or_none():
            should_add_node_as_child = (
                selected_node.has_children() and not selected_node.data.collapsed
            )
            if should_add_node_as_child:
                selected_node.prepend_child(new_node)
            else:
                if self._insertion_state == InsertionState.AFTER:
                    selected_node.add_sibling_after_self(new_node)
                else:
                    selected_node.add_sibling_before_self(new_node)
        else:
            self.tree_root.add_child(new_node)
        self._insertion_state = InsertionState.NOT_INSERTING
        self.selected_node = Optional.some(new_node)
        self._last_item_on_screen += 1

    def insertion_indent(self) -> int:
        if selected_node := self.selected_node.value_or_none():
            indent = selected_node.level - self.tree_root.level
            if selected_node.has_children() and not selected_node.data.collapsed:
                return indent
            return indent - 1
        return 0

    def start_edit(self):
        if self.selected_node.has_value():
            self._item_being_edited = Optional.some(
                copy.deepcopy(self.selected_node.value())
            )

    def cancel_edit(self):
        self._item_being_edited = Optional.none()

    def finish_edit(self, new_text: str):
        assert self.is_editing
        assert self.selected_node.has_value()
        self.selected_node.value().data.text = new_text
        self._item_being_edited = Optional.none()

    @property
    def is_editing(self):
        return self._item_being_edited.has_value()

    @property
    def is_searching(self):
        return self._search_string.has_value()

    def update_search(self, search_string: str):
        if search_string == "" and self._state_before_search.selected_node.is_none():
            self._state_before_search.selected_node = self.selected_node

        self._search_string = Optional.some(search_string)
        self._update_search_results()
        if self._search_results:
            self.selected_node = Optional.some(self._search_results[0])

        self._update_node_visibility()

    def cancel_search(self):
        self._search_string = Optional.none()
        self._search_results = []
        self._restore_search_state()

        self._update_node_visibility()

    def finish_search(self):
        self._search_string = Optional.none()
        self._search_results = []

    def select_next_search_result(self):
        for i, search_result in enumerate(self._search_results):
            if search_result == self.selected_node.value():
                self.selected_node = Optional.some(
                    self._search_results[(i + 1) % len(self._search_results)]
                )
                break

    def select_previous_search_result(self):
        for i, search_result in enumerate(self._search_results):
            if search_result == self.selected_node.value():
                self.selected_node = Optional.some(
                    self._search_results[(i - 1) % len(self._search_results)]
                )
                break

    def _is_search_result(self, node: TreeNode) -> bool:
        if not self.is_searching:
            return False
        return self._search_string.value().lower() in node.data.text.lower()

    def _update_search_results(self):
        if len(self._search_string.value_or("")) < 2:
            self._search_results = []
            return

        def uncollapse_parents(node):
            if node.parent.value().data.collapsed:
                node.parent.value().data.collapsed = False
                self._state_before_search.collapsed_nodes.append(node.parent.value())
                uncollapse_parents(node.parent.value())

        self._search_results = [
            node
            for node in self.tree_root.gen_all_nodes()
            if self._is_search_result(node)
        ]
        for result in self._search_results:
            uncollapse_parents(result)

    def _restore_search_state(self):
        self.selected_node = self._state_before_search.selected_node
        for node in self._state_before_search.collapsed_nodes:
            node.data.collapsed = True
        self._state_before_search = StateBeforeSearch(
            selected_node=Optional.none(), collapsed_nodes=[]
        )

    def toggle_complete(self):
        if self.selected_node.is_none():
            return

        # Need to move selection before completing, or select_previous will not work
        node_to_complete = self.selected_node
        if self._config_manager.hide_complete_items:
            self.select_previous()

        if not node_to_complete.value().data.complete:

            def set_complete(node):
                node.data.complete = True

            node_to_complete.value().apply_to_self_and_children(set_complete)
        else:
            node_to_complete.value().data.complete = False

        self._update_node_visibility()

    def index_of_selected_node(self) -> int:
        for index, item in enumerate(self._all_visible_nodes()):
            if self.selected_node.has_value() and (item == self.selected_node.value()):
                return index
        return 0

    def delete_item(self):
        self._push_undo_state()
        if node_to_remove := self.selected_node.value_or_none():
            self._cut_item = Optional.some(node_to_remove)
            self.select_previous()
            self.tree_root.remove_node(node_to_remove)
            self.select_next()
            if not self.tree_root.has_children():
                self.selected_node = Optional.none()

    def paste_item(self, before=False):
        if self._cut_item.is_none():
            return

        if self.selected_node.has_value():
            if before:
                self.selected_node.value().add_sibling_before_self(
                    self._cut_item.value()
                )
            else:
                self.selected_node.value().add_sibling_after_self(
                    self._cut_item.value()
                )
        else:
            self.tree_root.add_child(self._cut_item.value())
        self._cut_item.value().update_level_to_parent()
        self._cut_item = Optional.none()

    def undo(self):
        if not self._undo_stack:
            return

        tree_root_index = self.tree_root.root().index_for_node(self.tree_root)
        selected_node_index = (  # TODO: clean up
            None
            if self.selected_node.is_none()
            else self.tree_root.root().index_for_node(self.selected_node.value())
        )

        undo_state = self._undo_stack.pop()
        self.tree_root = undo_state

        if tree_root_index.has_value():
            self.set_as_root(
                self.tree_root.root().node_at_index(tree_root_index.value())
            )
        if selected_node_index.has_value():
            self.selected_node = self.tree_root.root().node_at_index(
                selected_node_index.value()
            )

        self._update_node_visibility()

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
        return self.tree_root.gen_all_visible_nodes()

    def _update_node_visibility(self):
        def node_is_visible(node: TreeNode) -> bool:
            # Always hide completed items if hide_complete is set
            if self._config_manager.hide_complete_items and node.data.complete:
                return False
            # Hide children of collapsed nodes
            if node.parent.has_value() and node.parent.value().data.collapsed:
                return False
            # Make sure we hide all children of hidden nodes
            if node.parent.has_value() and not node_is_visible(node.parent.value()):
                return False
            return True

        for node in self.tree_root.root().gen_all_nodes():
            node.visible = node_is_visible(node)

    def _push_undo_state(self):
        saved_tree = copy.deepcopy(self.tree_root.root())
        self._undo_stack.append(saved_tree)

    def _label_display_text(self, text: str, indent: int, is_selected: bool) -> str:
        if is_selected:
            return text

        limit = self._width - indent * 3 - 2  # TODO: this should use INDENT_SPACES
        if len(text) > (limit - 3):
            return text[: limit - 3] + "..."
        return text
