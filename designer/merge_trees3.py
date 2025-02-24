def merge_space_data(god_tree, updated_nodes):
    """
    Insert space data from updated nodes into the God tree for matching node IDs,
    while preserving ALL original details of the God tree.
    
    Args:
        god_tree (dict): The original "God tree" structure with a 'nodes' key
        updated_nodes (list or dict): Updated nodes with space data, either as a list of nodes 
                                     or a single node object with 'id', 'space', and 'children'
    
    Returns:
        dict: The updated God tree with space data merged in
    """
    # Create a deep copy to avoid modifying the original tree
    import copy
    result_tree = copy.deepcopy(god_tree)
    
    # Convert updated_nodes to a list if it's a single node dictionary
    node_list = [updated_nodes] if isinstance(updated_nodes, dict) else updated_nodes
    
    # Process each updated node
    for updated_node in node_list:
        node_id = updated_node.get('id')
        
        # Find matching node in the God tree
        if node_id and node_id in result_tree['nodes']:
            # Update space data
            if 'space' in updated_node and 'document' in result_tree['nodes'][node_id]:
                # Convert 'space' to appropriate format for the God tree
                space_data = convert_space_format(updated_node['space'])
                result_tree['nodes'][node_id]['document']['size'] = space_data
            
            # Process children recursively
            if 'children' in updated_node:
                process_children(result_tree, node_id, updated_node['children'])
    
    return result_tree

def convert_space_format(space_data):
    """
    Convert from {left, right, top, bottom} format to {x, y, width, height} format.
    
    Args:
        space_data (dict): Space data in format {left, right, top, bottom}
        
    Returns:
        dict: Space data in format {x, y, width, height}
    """
    # Assuming left = x, top = y, and calculating width and height
    x = space_data.get('left', 0)
    y = space_data.get('top', 0)
    
    # Calculate width and height from left/right, top/bottom values
    width = space_data.get('right', 0) - x
    height = space_data.get('bottom', 0) - y
    
    return {
        'x': x,
        'y': y,
        'width': width,
        'height': height
    }

def process_children(god_tree, parent_id, updated_children):
    """
    Process updated children and update corresponding children in the God tree.
    
    Args:
        god_tree (dict): The God tree being updated
        parent_id (str): ID of the parent node
        updated_children (list): List of updated child nodes
    """
    if not updated_children or parent_id not in god_tree['nodes']:
        return
    
    # Get God tree children for this parent
    if 'document' in god_tree['nodes'][parent_id] and 'children' in god_tree['nodes'][parent_id]['document']:
        god_children = god_tree['nodes'][parent_id]['document']['children']
        
        # Create a map of children by ID for quick lookup
        god_children_map = {child.get('id'): (i, child) for i, child in enumerate(god_children) if 'id' in child}
        
        # Update each child in the God tree
        for updated_child in updated_children:
            if 'id' in updated_child and updated_child['id'] in god_children_map:
                index, god_child = god_children_map[updated_child['id']]
                
                # Update space data
                if 'space' in updated_child:
                    god_children[index]['size'] = convert_space_format(updated_child['space'])
                
                # Process this child's children recursively
                if 'children' in updated_child:
                    # If this child is also a node in the God tree, process its children
                    if updated_child['id'] in god_tree['nodes']:
                        process_children(god_tree, updated_child['id'], updated_child['children'])
                    # Otherwise, just update the children within this child object
                    elif 'children' in god_child:
                        update_nested_children(god_child['children'], updated_child['children'])

def update_nested_children(god_children, updated_children):
    """
    Update nested children that aren't separate nodes in the God tree.
    
    Args:
        god_children (list): List of children from the God tree
        updated_children (list): List of updated children
    """
    # Create maps for quick lookup
    god_map = {child.get('id'): (i, child) for i, child in enumerate(god_children) if 'id' in child}
    
    for updated_child in updated_children:
        if 'id' in updated_child and updated_child['id'] in god_map:
            index, god_child = god_map[updated_child['id']]
            
            # Update space data
            if 'space' in updated_child:
                god_children[index]['size'] = convert_space_format(updated_child['space'])
            
            # Recursively update children
            if 'children' in updated_child and 'children' in god_child:
                update_nested_children(god_child['children'], updated_child['children'])


# Test with your specific structure
def test_with_specific_structure():
    # Sample God tree with nodes structure
    god_tree = {
        "name": "Car Rent Website Design - Pickolab Studio (Community)",
        "nodes": {
            "44:16200": {
                "document": {
                    "id": "44:16200",
                    "name": "Reviews",
                    "clipsContent": True,
                    "children": [
                        {
                            "id": "44:16201",
                            "name": "Total Review",
                            "layoutMode": "HORIZONTAL",
                            "itemSpacing": 12
                        }
                    ]
                }
            },
            "44:16201": {
                "document": {
                    "id": "44:16201",
                    "name": "Total Review",
                    "children": [
                        {
                            "id": "44:16202",
                            "name": "Reviews"
                        },
                        {
                            "id": "44:16203",
                            "name": "Total Review"
                        }
                    ]
                }
            }
        }
    }
    
    # Updated node with the structure you described
    updated_node = {
        "id": "44:16200",
        "space": {
            "left": 24,
            "right": 856,
            "top": 24,
            "bottom": 32
        },
        "children": [
            {
                "id": "44:16201",
                "space": {
                    "left": 0, 
                    "right": 12,
                    "top": 0,
                    "bottom": 0
                },
                "children": [
                    {
                        "id": "44:16202",
                        "space": {
                            "left": 0,
                            "right": 80,
                            "top": 0,
                            "bottom": 28
                        }
                    },
                    {
                        "id": "44:16203",
                        "space": {
                            "left": 12,
                            "right": 12,
                            "top": 6,
                            "bottom": 6
                        }
                    }
                ]
            }
        ]
    }
    
    # Merge the space data
    result = merge_space_data(god_tree, updated_node)
    
    # Verify the God tree structure is preserved
    assert result["name"] == "Car Rent Website Design - Pickolab Studio (Community)"
    assert "44:16200" in result["nodes"]
    assert result["nodes"]["44:16200"]["document"]["name"] == "Reviews"
    assert result["nodes"]["44:16200"]["document"]["clipsContent"] == True
    
    # Verify space data was added
    assert "size" in result["nodes"]["44:16200"]["document"]
    expected_size = {"x": 24, "y": 24, "width": 832, "height": 8}
    assert result["nodes"]["44:16200"]["document"]["size"] == expected_size
    
    # Verify children data was updated
    child = result["nodes"]["44:16200"]["document"]["children"][0]
    assert child["id"] == "44:16201"
    assert child["layoutMode"] == "HORIZONTAL"
    assert child["size"] == {"x": 0, "y": 0, "width": 12, "height": 0}
    
    # Verify second level children
    grandchildren = result["nodes"]["44:16201"]["document"]["children"]
    assert grandchildren[0]["id"] == "44:16202"
    assert grandchildren[0]["size"] == {"x": 0, "y": 0, "width": 80, "height": 28}
    assert grandchildren[1]["id"] == "44:16203"
    assert grandchildren[1]["size"] == {"x": 12, "y": 6, "width": 0, "height": 0}
    
    print("Test with specific structure passed!")

# Run the test
if __name__ == "__main__":
    test_with_specific_structure()