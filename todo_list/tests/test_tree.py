from todo_list.tree import TreeNode


def test_add_tree_nodes():
    root = TreeNode("root")
    branch1 = TreeNode("branch1")
    branch2 = TreeNode("branch2")
    leaf = TreeNode("leaf")
    root.add_child(branch1)
    root.add_child(branch2)
    branch1.add_child(leaf)

    assert len(root.children) == 2
    assert len(branch1.children) == 1
    assert root.level == 0
    assert branch1.level == 1
    assert branch2.level == 1
    assert leaf.level == 2
    assert leaf.parent == branch1
    assert branch1.parent == root
    assert branch2.parent == root
    assert branch1.root() == root
    assert branch2.root() == root
    assert leaf.root() == root

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


def test_gen_all_items():
    root = TreeNode("root")
    branch = TreeNode("branch")
    leaf = TreeNode("leaf")
    root.add_child(branch)
    branch.add_child(leaf)

    generator = root.gen_all_nodes()
    first = next(generator)
    second = next(generator)
    third = next(generator)

    assert first == root
    assert second == branch
    assert third == leaf


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
