from typing import Dict, Any, Optional
from copy import deepcopy

def find_node_by_id(tree: Dict[str, Any], search_id: str) -> Optional[Dict[str, Any]]:
    """
    Recursively find a node by its ID in a tree structure.
    
    Args:
        tree: The tree or subtree to search in
        search_id: The ID to search for
    
    Returns:
        The found node or None if not found
    """
    if isinstance(tree, dict):
        if tree.get('id') == search_id:
            return tree
        # Recursively search in children if they exist
        if 'children' in tree and isinstance(tree['children'], list):
            for child in tree['children']:
                result = find_node_by_id(child, search_id)
                if result:
                    return result

    return None  # Ensure None is returned if no match is found

    

def merge_space_data(space_tree: Dict[str, Any], root_node: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges space data from a space tree into a node tree structure.
    
    Args:
        space_tree: Tree structure containing space information
        root_node: Root node of the tree to be updated
    
    Returns:
        Updated tree with merged space data
    """
    updated_tree = deepcopy(root_node)

    def process_space_node(space_node: Dict[str, Any]) -> None:
        """Recursively process nodes from the space tree and update corresponding nodes"""
        node_id = space_node.get('id')
        if node_id:
            # Find the corresponding node in our tree
            target_node = find_node_by_id(updated_tree, node_id)
            
            if target_node:
                # Update space data
                space_data = space_node.get('space')
                if space_data:
                    target_node['space'] = {
                        'left': space_data['left'],
                        'right': space_data['right'],
                        'top': space_data['top'],
                        'bottom': space_data['bottom']
                    }
        
        # Process children recursively
        for child in space_node.get('children', []):
            process_space_node(child)

    # Process the entire tree
    process_space_node(space_tree)
    
    
    return updated_tree

# Example usage:
if __name__ == "__main__":
    space_tree = {
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
                "children": []
            }
        ]
    }
    
    root_node = {
        "id": "44:16200",
        "document": {
            "id": "44:16200",
            "name": "Reviews"
        },
        "children": [
            {
                "id": "44:16201",
                "name": "Total Review",
                "layoutMode": "HORIZONTAL"
            }
        ]
    }
    
    result = merge_space_data(space_tree, root_node)
    print(result)