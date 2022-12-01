import pytest

from todo_list.tree import TreeNode


@pytest.fixture
def tree_and_nodes():
    # - root
    #   - branch1
    #     - leaf1
    #   - leaf2
    #   - branch2
    #     - leaf3

    root = TreeNode("root")
    branch1 = TreeNode("branch1")
    branch2 = TreeNode("branch2")
    leaf1 = TreeNode("leaf1")
    leaf2 = TreeNode("leaf2")
    leaf3 = TreeNode("leaf3")
    root.add_child(branch1)
    root.add_child(branch2)
    root.add_child(leaf2, after_child=branch1)
    branch1.add_child(leaf1)
    branch2.add_child(leaf3)

    nodes = {
        "root": root,
        "branch1": branch1,
        "branch2": branch2,
        "leaf1": leaf1,
        "leaf2": leaf2,
        "leaf3": leaf3,
    }
    return root, nodes


def test_add_tree_nodes(tree_and_nodes):
    root, nodes = tree_and_nodes

    branch1 = nodes["branch1"]
    branch2 = nodes["branch2"]
    leaf1 = nodes["leaf1"]
    leaf2 = nodes["leaf2"]

    assert len(root.children) == 3
    assert len(branch1.children) == 1
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

    root.add_child(branch1)
    branch1.add_sibling(branch2)

    assert root.children == [branch1, branch2]
    assert not branch1.children
    assert not branch2.children


def test_node_after():
    root = TreeNode("root")
    branch = TreeNode("branch")
    leaf1 = TreeNode("leaf1")
    leaf2 = TreeNode("leaf2")
    root.add_child(branch)
    branch.add_child(leaf1)
    branch.add_child(leaf2)

    assert root.node_after(branch) == leaf1
    assert root.node_after(leaf1) == leaf2
    assert root.node_after(leaf2) == branch


def test_node_before():
    root = TreeNode("root")
    branch = TreeNode("branch")
    leaf1 = TreeNode("leaf1")
    leaf2 = TreeNode("leaf2")
    root.add_child(branch)
    branch.add_child(leaf1)
    branch.add_child(leaf2)

    assert root.node_before(branch) == leaf2
    assert root.node_before(leaf1) == branch
    assert root.node_before(leaf2) == leaf1


def test_change_level():
    root = TreeNode("root")
    branch1 = TreeNode("branch1")
    branch2 = TreeNode("branch2")
    leaf1 = TreeNode("leaf1")
    leaf2 = TreeNode("leaf2")
    root.add_child(branch1)
    root.add_child(branch2)
    branch1.add_child(leaf1)
    leaf1.add_child(leaf2)

    root.change_level(-1)

    assert root.level == -1
    assert branch1.level == 0
    assert branch2.level == 0
    assert leaf1.level == 1
    assert leaf2.level == 2


def test_gen_all_nodes(tree_and_nodes):
    root, nodes = tree_and_nodes

    generator = root.gen_all_nodes()
    expected_output = ["branch1", "leaf1", "leaf2", "branch2", "leaf3"]

    for output, expected in zip(generator, expected_output):
        assert output.data == expected


def test_gen_all_nodes_with_condition(tree_and_nodes):
    root, nodes = tree_and_nodes

    def filter(node):
        return node.data != "branch1"

    generator = root.gen_all_nodes_with_condition(filter)
    expected_output = ["branch1", "leaf2", "branch2", "leaf3"]

    for output, expected in zip(generator, expected_output):
        assert output.data == expected


def test_remove_child():
    root = TreeNode("root")
    branch1 = TreeNode("branch1")
    branch2 = TreeNode("branch2")
    leaf1 = TreeNode("leaf1")
    leaf2 = TreeNode("leaf2")
    root.add_child(branch1)
    root.add_child(branch2)
    branch1.add_child(leaf1)
    leaf1.add_child(leaf2)

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
    root.add_child(leaf1)
    root.add_child(leaf2)

    expected = "- root\n  - leaf1\n  - leaf2"

    result = str(root)

    assert result == expected


def test_apply_to_children():
    root = TreeNode("root")
    branch = TreeNode("branch")
    leaf1 = TreeNode("leaf1")
    leaf2 = TreeNode("leaf2")
    root.add_child(branch)
    branch.add_child(leaf1)
    branch.add_child(leaf2)

    def complete(node):
        node.data = "updated"

    branch.apply_to_children(complete)

    assert root.data == "root"
    assert branch.data == "updated"
    assert leaf1.data == "updated"
    assert leaf2.data == "updated"
