def merge_space_data(god_tree, new_tree):
    """
    Insert space data from a new tree into the God tree for matching node IDs.
    
    Args:
        god_tree (dict): The original "God tree" structure
        new_tree (dict): A new tree with matching IDs and space data to be inserted
        
    Returns:
        dict: The updated God tree with space data merged in
    """
    # Create a deep copy to avoid modifying the original tree
    import copy
    updated_tree = copy.deepcopy(god_tree)
    
    # Process nodes in the new tree
    for node_id, node_data in new_tree.get("nodes", {}).items():
        # Check if this node exists in the God tree
        if node_id in updated_tree.get("nodes", {}):
            # Extract space data if it exists
            if "size" in node_data:
                # Add or update the space data in the God tree
                if "document" in updated_tree["nodes"][node_id]:
                    updated_tree["nodes"][node_id]["document"]["size"] = node_data["size"]
                else:
                    # Create document if it doesn't exist
                    if "document" not in updated_tree["nodes"][node_id]:
                        updated_tree["nodes"][node_id]["document"] = {}
                    updated_tree["nodes"][node_id]["document"]["size"] = node_data["size"]
                    
            # Process children recursively if they exist
            process_children(updated_tree, new_tree, node_id)
    
    return updated_tree

def process_children(god_tree, new_tree, parent_id):
    """
    Recursively process children of a node to update their space data.
    
    Args:
        god_tree (dict): The God tree being updated
        new_tree (dict): The new tree containing space data
        parent_id (str): The ID of the parent node being processed
    """
    # Check if the parent exists in both trees and has children
    if "document" in god_tree["nodes"][parent_id] and "children" in god_tree["nodes"][parent_id]["document"]:
        god_children = god_tree["nodes"][parent_id]["document"]["children"]
        
        # Get new tree node children if they exist
        new_node = new_tree["nodes"].get(parent_id, {})
        if "children" in new_node.get("document", {}):
            new_children = new_node["document"]["children"]
            
            # Map new children by ID for easy lookup
            new_children_map = {child["id"]: child for child in new_children if "id" in child}
            
            # Update each child in the God tree
            for i, child in enumerate(god_children):
                if child["id"] in new_children_map:
                    # Update size if it exists
                    if "size" in new_children_map[child["id"]]:
                        god_children[i]["size"] = new_children_map[child["id"]]["size"]
                    
                    # Recursively process this child's children
                    # We need to ensure the child exists as a node in both trees
                    if child["id"] in god_tree["nodes"] and child["id"] in new_tree["nodes"]:
                        process_children(god_tree, new_tree, child["id"])


# Test cases
def test_merge_space_data():
    # Test case 1: Basic tree with space data
    god_tree = {
        "name": "Test God Tree",
        "nodes": {
            "1": {
                "document": {
                    "id": "1",
                    "name": "Root",
                    "children": [
                        {
                            "id": "2",
                            "name": "Child"
                        }
                    ]
                }
            },
            "2": {
                "document": {
                    "id": "2",
                    "name": "Child"
                }
            }
        }
    }
    
    new_tree = {
        "name": "Test New Tree",
        "nodes": {
            "1": {
                "size": {"x": 10, "y": 20, "width": 100, "height": 50}
            },
            "2": {
                "size": {"x": 30, "y": 40, "width": 60, "height": 30}
            }
        }
    }
    
    result = merge_space_data(god_tree, new_tree)
    
    # Verify the results
    assert result["nodes"]["1"]["document"]["size"] == {"x": 10, "y": 20, "width": 100, "height": 50}
    assert result["nodes"]["2"]["document"]["size"] == {"x": 30, "y": 40, "width": 60, "height": 30}
    print("Test case 1 passed!")
    
    # Test case 2: Nested children with space data
    god_tree = {
        "name": "Nested God Tree",
        "nodes": {
            "parent": {
                "document": {
                    "id": "parent",
                    "name": "Parent",
                    "children": [
                        {
                            "id": "child1",
                            "name": "Child 1"
                        },
                        {
                            "id": "child2",
                            "name": "Child 2"
                        }
                    ]
                }
            },
            "child1": {
                "document": {
                    "id": "child1",
                    "name": "Child 1",
                    "children": [
                        {
                            "id": "grandchild",
                            "name": "Grand Child"
                        }
                    ]
                }
            },
            "child2": {
                "document": {
                    "id": "child2",
                    "name": "Child 2"
                }
            },
            "grandchild": {
                "document": {
                    "id": "grandchild",
                    "name": "Grand Child"
                }
            }
        }
    }
    
    new_tree = {
        "name": "Nested New Tree",
        "nodes": {
            "parent": {
                "size": {"x": 0, "y": 0, "width": 200, "height": 300},
                "document": {
                    "children": [
                        {
                            "id": "child1",
                            "size": {"x": 10, "y": 10, "width": 90, "height": 90}
                        },
                        {
                            "id": "child2",
                            "size": {"x": 110, "y": 10, "width": 90, "height": 90}
                        }
                    ]
                }
            },
            "child1": {
                "size": {"x": 10, "y": 10, "width": 90, "height": 90},
                "document": {
                    "children": [
                        {
                            "id": "grandchild",
                            "size": {"x": 20, "y": 20, "width": 70, "height": 40}
                        }
                    ]
                }
            },
            "grandchild": {
                "size": {"x": 20, "y": 20, "width": 70, "height": 40}
            }
        }
    }
    
    result = merge_space_data(god_tree, new_tree)
    
    # Verify the results
    assert result["nodes"]["parent"]["document"]["size"] == {"x": 0, "y": 0, "width": 200, "height": 300}
    assert result["nodes"]["child1"]["document"]["size"] == {"x": 10, "y": 10, "width": 90, "height": 90}
    assert result["nodes"]["grandchild"]["document"]["size"] == {"x": 20, "y": 20, "width": 70, "height": 40}
    
    # Verify that children within the parent document were updated
    parent_children = result["nodes"]["parent"]["document"]["children"]
    assert any(child["id"] == "child1" and child["size"] == {"x": 10, "y": 10, "width": 90, "height": 90} 
               for child in parent_children)
    assert any(child["id"] == "child2" and child["size"] == {"x": 110, "y": 10, "width": 90, "height": 90} 
               for child in parent_children)
    
    # Verify that grandchild within child1 document was updated
    child1_children = result["nodes"]["child1"]["document"]["children"]
    assert any(child["id"] == "grandchild" and child["size"] == {"x": 20, "y": 20, "width": 70, "height": 40} 
               for child in child1_children)
    
    print("Test case 2 passed!")
    print("All tests passed!")

# Run the tests
if __name__ == "__main__":
    test_merge_space_data()