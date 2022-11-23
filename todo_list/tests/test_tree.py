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
