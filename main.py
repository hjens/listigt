from todo_list import tree, todo_list

FILENAME = "test.txt"


with open(FILENAME) as f:
    list = tree.tree_nodes_from_string(f.read(), todo_list.TodoItem.tree_node_from_str, log=False)


list_as_str = "".join([f"{i}" for i in list])

list2 = tree.tree_nodes_from_string(list_as_str, todo_list.TodoItem.tree_node_from_str, log=True)

#list_as_str2 = "".join([f"{i}" for i in list2])

#print(list_as_str2)
