import json

import json

def extract_nodes(node, parent=None):
    """
    Recursively extracts nodes as simplified dictionaries (with just x, y, etc.)
    and passes the simplified parent to children.
    """
    extracted = []
    simplified_node = None

    # Simplify the node if it has a size.
    if 'size' in node:
        simplified_node = {
            'name': node.get('name', 'Unnamed'),
            'x': node['size'].get('x', 0),
            'y': node['size'].get('y', 0),
            'width': node['size'].get('width', 0),
            'height': node['size'].get('height', 0),
            'paddingLeft': node.get('paddingLeft'),
            'paddingTop': node.get('paddingTop'),
            'parent': parent  # simplified parent, if available
        }
        extracted.append(simplified_node)
    else:
        # If there is no size, pass the current parent along.
        simplified_node = parent

    # Process children using the simplified node as the parent.
    if 'children' in node and isinstance(node['children'], list):
        for child in node['children']:
            extracted.extend(extract_nodes(child, parent=simplified_node))
    
    return extracted

def calculate_spacing(parent, child, default_padding=0):
    """
    Calculates spacing between a parent and a child node.
    Two approaches are calculated:
    
    1. Strict geometric margin:
       - left: difference in x coordinates
       - top: difference in y coordinates
       
    2. Auto layout based:
       - Uses the parent's padding to adjust the offset.
    """
    parent_x = parent.get('x', 0)
    parent_y = parent.get('y', 0)
    child_x = child.get('x', 0)
    child_y = child.get('y', 0)

    # Strict geometric margin
    strict_margin_left = child_x - parent_x
    strict_margin_top = child_y - parent_y

    # Use parent’s padding if set, otherwise default_padding.
    parent_padding_left = parent.get('paddingLeft', default_padding) or default_padding
    parent_padding_top = parent.get('paddingTop', default_padding) or default_padding

    # Auto layout margin calculation (normalized relative to parent's padded origin)
    auto_layout_margin_left = child_x - (parent_x + parent_padding_left)
    auto_layout_margin_top = child_y - (parent_y + parent_padding_top)
    
    return {
        'child_name': child.get('name', 'Unnamed'),
        'strict_margin': {
            'left': strict_margin_left,
            'top': strict_margin_top
        },
        'auto_layout_based': {
            'parent_padding': {
                'left': parent_padding_left,
                'top': parent_padding_top
            },
            'margin': {
                'left': auto_layout_margin_left,
                'top': auto_layout_margin_top
            }
        }
    }

def process_json_file(filename, default_padding=0):
    # Load JSON file
    with open(filename, 'r') as f:
        figma_data = json.load(f)
    
    # Extract nodes recursively, starting from the document node.
    # Assumes the JSON structure as given.
    document = list(figma_data["nodes"].values())[0]["document"]
    nodes = extract_nodes(document)
    
    results = []
    # Loop through nodes and calculate spacing for nodes with a parent reference.
    for node in nodes:
        if node.get('parent') is not None:
            parent_node = node['parent']
            spacing = calculate_spacing(parent_node, node, default_padding)
            results.append(spacing)
    
    return results

if __name__ == '__main__':
    # Replace with your actual JSON file path
    filename = 'test/data.json'
    spacing_results = process_json_file(filename, default_padding=20)
    
    # Print out the calculated spacing options
    for result in spacing_results:
        print(f"Node: {result['child_name']}")
        print("  Strict Margin:", result['strict_margin'])
        print("  Auto Layout Based:", result['auto_layout_based'])
        print()


def process_json_file(filename, default_padding=0):
    # Load JSON file
    with open(filename, 'r') as f:
        figma_data = json.load(f)
    
    # Extract nodes recursively
    nodes = extract_nodes(list(figma_data["nodes"].values())[0]["document"])

    
    # Organize nodes by their parent geometry if available
    results = []
    # Loop through nodes and calculate spacing for nodes that have a parent reference.
    for node in nodes:
        if node.get('parent') is not None:
            # node['parent'] is the parent's size dict (with x and y)
            parent_node = {
                'x': node['parent'].get('x', 0),
                'y': node['parent'].get('y', 0),
                'paddingLeft': figma_data.get('paddingLeft', default_padding),  # fallback if parent's padding is not in the node
                'paddingTop': figma_data.get('paddingTop', default_padding)
            }
            spacing = calculate_spacing(parent_node, node, default_padding)
            results.append(spacing)
    
    return results

if __name__ == '__main__':
    # Replace 'data.json' with your actual JSON file path
    filename = 'test/data.json'
    spacing_results = process_json_file(filename, default_padding=20)
    
    # Print out the calculated spacing options
    for result in spacing_results:
        print(f"Node: {result['child_name']}")
        print("  Strict Margin:", result['strict_margin'])
        print("  Auto Layout Based:", result['auto_layout_based'])
        print()
