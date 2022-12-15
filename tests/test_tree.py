from copy import copy

import pytest

from src.listigt.todo_list.tree import TreeNode


@pytest.fixture
def tree_and_nodes():
    # - root
    #   - branch1
    #     - sub_branch
    #       - leaf3
    #     - leaf1
    #   - leaf2
    #   - branch2
    #     - leaf4

    root = TreeNode("root")
    branch1 = TreeNode("branch1")
    branch2 = TreeNode("branch2")
    leaf1 = TreeNode("leaf1")
    leaf2 = TreeNode("leaf2")
    sub_branch = TreeNode("sub_branch")
    leaf3 = TreeNode("leaf3")
    leaf4 = TreeNode("leaf4")
    root.append_child(branch1)
    root.append_child(branch2)
    root.append_child(leaf2, after_child=branch1)
    branch1.append_child(sub_branch)
    sub_branch.append_child(leaf3)
    branch1.append_child(leaf1)
    branch2.append_child(leaf4)

    nodes = {
        "root": root,
        "branch1": branch1,
        "branch2": branch2,
        "sub_branch": sub_branch,
        "leaf1": leaf1,
        "leaf2": leaf2,
        "leaf3": leaf3,
        "leaf4": leaf4,
    }
    return root, nodes


def test_add_tree_nodes(tree_and_nodes):
    root, nodes = tree_and_nodes

    branch1 = nodes["branch1"]
    branch2 = nodes["branch2"]
    leaf1 = nodes["leaf1"]
    leaf2 = nodes["leaf2"]

    assert len(root.children) == 3
    assert len(branch1.children) == 2
    assert root.children == [branch1, leaf2, branch2]
    assert root.level == 0
    assert branch1.level == 1
    assert branch2.level == 1
    assert leaf1.level == 2
    assert leaf1.parent == branch1
    assert branch1.parent == root
    assert branch2.parent == root
    assert branch1.root() == root
    assert branch2.root() == root
    assert leaf1.root() == root


def test_add_sibling():
    root = TreeNode("root")
    branch1 = TreeNode("branch1")
    branch2 = TreeNode("branch2")

    root.append_child(branch1)
    branch1.add_sibling(branch2)

    assert root.children == [branch1, branch2]
    assert not branch1.children
    assert not branch2.children

def test_prepend_child(tree_and_nodes):
    root, nodes = tree_and_nodes
    nodes["branch1"].prepend_child(TreeNode("new_node"))

    assert nodes["branch1"].first_child().data == "new_node"


def test_node_after(tree_and_nodes):
    root, nodes = tree_and_nodes

    assert root.node_after(nodes["branch1"]) == nodes["sub_branch"]
    assert root.node_after(nodes["leaf1"]) == nodes["leaf2"]
    assert root.node_after(nodes["leaf4"]) == nodes["branch1"]


def test_node_after_with_condition(tree_and_nodes):
    root, nodes = tree_and_nodes
    filter = lambda node: node.data != "sub_branch"

    assert root.node_after(nodes["branch1"], filter) == nodes["leaf1"]
    assert root.node_after(nodes["leaf4"], filter) == nodes["branch1"]


def test_node_before(tree_and_nodes):
    root, nodes = tree_and_nodes

    assert root.node_before(nodes["sub_branch"]) == nodes["branch1"]
    assert root.node_before(nodes["leaf1"]) == nodes["leaf3"]
    assert root.node_before(nodes["branch1"]) == nodes["leaf4"]


def test_node_before_with_condition(tree_and_nodes):
    root, nodes = tree_and_nodes
    filter = lambda node: node.data != "sub_branch"

    assert root.node_before(nodes["leaf1"], filter) == nodes["branch1"]
    assert root.node_before(nodes["branch1"], filter) == nodes["leaf4"]


def test_change_level():
    # TODO: use fixture
    root = TreeNode("root")
    branch1 = TreeNode("branch1")
    branch2 = TreeNode("branch2")
    leaf1 = TreeNode("leaf1")
    leaf2 = TreeNode("leaf2")
    root.append_child(branch1)
    root.append_child(branch2)
    branch1.append_child(leaf1)
    leaf1.append_child(leaf2)

    root.change_level(-1)

    assert root.level == -1
    assert branch1.level == 0
    assert branch2.level == 0
    assert leaf1.level == 1
    assert leaf2.level == 2


def test_gen_all_nodes(tree_and_nodes):
    root, nodes = tree_and_nodes

    generator = root.gen_all_nodes()
    expected_output = [
        "branch1",
        "sub_branch",
        "leaf3",
        "leaf1",
        "leaf2",
        "branch2",
        "leaf4",
    ]

    for output, expected in zip(generator, expected_output):
        assert output.data == expected


def test_gen_all_nodes_with_condition(tree_and_nodes):
    root, nodes = tree_and_nodes

    def filter(node):
        return node.data != "sub_branch"

    generator = root.gen_all_nodes_with_condition(filter)
    expected_output = ["branch1", "leaf1", "leaf2", "branch2", "leaf4"]

    for output, expected in zip(generator, expected_output):
        assert output.data == expected


def test_gen_all_nodes_with_complex_condition(tree_and_nodes):
    root, nodes = tree_and_nodes

    def filter(node):
        return node.parent.data != "sub_branch"

    generator = root.gen_all_nodes_with_condition(filter)
    expected_output = ["branch1", "sub_branch", "leaf1", "leaf2", "branch2", "leaf4"]

    for output, expected in zip(generator, expected_output):
        assert output.data == expected



def test_node_at_index(tree_and_nodes):
    root, nodes = tree_and_nodes
    assert root.node_at_index(3) == nodes["leaf1"]
    assert root.node_at_index(100) is None


def test_index_for_node(tree_and_nodes):
    root, nodes = tree_and_nodes
    assert root.index_for_node(nodes["leaf1"]) == 3


def test_remove_child():
    # TODO: use fixture
    root = TreeNode("root")
    branch1 = TreeNode("branch1")
    branch2 = TreeNode("branch2")
    leaf1 = TreeNode("leaf1")
    leaf2 = TreeNode("leaf2")
    root.append_child(branch1)
    root.append_child(branch2)
    branch1.append_child(leaf1)
    leaf1.append_child(leaf2)

    assert leaf1 in branch1.children
    root.remove_node(leaf1)
    assert leaf1 not in branch1.children

    assert branch2 in root.children
    root.remove_node(branch2)
    assert branch2 not in root.children


def test_to_str():
    root = TreeNode("root")
    leaf1 = TreeNode("leaf1")
    leaf2 = TreeNode("leaf2")
    root.append_child(leaf1)
    root.append_child(leaf2)

    expected = "- root\n  - leaf1\n  - leaf2"

    result = str(root)

    assert result == expected


def test_apply_to_self_and_children(tree_and_nodes):
    root, nodes = tree_and_nodes

    def complete(node):
        node.data = "updated"

    nodes["branch1"].apply_to_self_and_children(complete)

    assert root.data == "root"
    assert nodes["branch1"].data == "updated"
    assert nodes["sub_branch"].data == "updated"
    assert nodes["leaf3"].data == "updated"
    assert nodes["leaf1"].data == "updated"


def test_copy():
    node = TreeNode("test")
    copied_node = copy(node)
    copied_node.data = "changed"

    assert node.data == "test"
    assert copied_node.data == "changed"