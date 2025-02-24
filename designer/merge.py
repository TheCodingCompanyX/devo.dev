import json

def find_and_insert_data(json_data, target_id, new_data):
    """
    Traverses the JSON data to find the node with the specified ID and inserts new data into its children.

    :param json_data: The JSON data to traverse.
    :param target_id: The ID of the node to find.
    :param new_data: The new data to insert into the children of the found node.
    :return: The modified JSON data.
    """
    if isinstance(json_data, dict):
        if json_data.get('id') == target_id:
            json_data['space'].append(new_data)
            return json_data
        for key, value in json_data.items():
            json_data[key] = find_and_insert_data(value, target_id, new_data)
    elif isinstance(json_data, list):
        for i, item in enumerate(json_data):
            json_data[i] = find_and_insert_data(item, target_id, new_data)
    return json_data

def merge_space_data(god_tree, new_tree):
    """
    Merges the space data from the new tree into the corresponding node in the god tree.

    :param god_tree: The god tree data.
    :param new_tree: The new tree data.
    :return: The updated god tree.
    """
    
    def find_and_update_node(tree, node_id, space_data):
        """Recursively finds a node by ID and updates its space data."""
        if tree.get("id") == node_id:
            tree["space"] = space_data
            return True
        
        for child in tree.get("children", []):
            if find_and_update_node(child, node_id, space_data):
                return True
        
        return False
    
    for node in new_tree.get("children", []):
        node_id = node.get("id")
        space_data = node.get("space")
        if node_id and space_data:
            print(f"Inserting space data into node {node_id}")
            find_and_update_node(god_tree, node_id, space_data)
        
        # Recursively process children
        if "children" in node:
            merge_space_data(god_tree, node)
    
    return god_tree

