import json
from collections import defaultdict

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
            'paddingRight': node.get('paddingRight'),
            'paddingBottom': node.get('paddingBottom'),
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

def calculate_parent_padding(parent, children):
    """
    Calculate the parent's padding based on the positions of all its children.
    Padding is calculated for all four sides: left, top, right, and bottom.
    """
    if not children:
        return {
            'paddingLeft': 0,
            'paddingTop': 0,
            'paddingRight': 0,
            'paddingBottom': 0
        }

    # Calculate left and top padding
    padding_left = min(child['x'] - parent['x'] for child in children)
    padding_top = min(child['y'] - parent['y'] for child in children)

    # Calculate right and bottom padding
    padding_right = min((parent['x'] + parent['width']) - (child['x'] + child['width']) for child in children)
    padding_bottom = min((parent['y'] + parent['height']) - (child['y'] + child['height']) for child in children)

    return {
        'paddingLeft': max(padding_left, 0),  # Ensure padding is not negative
        'paddingTop': max(padding_top, 0),
        'paddingRight': max(padding_right, 0),
        'paddingBottom': max(padding_bottom, 0)
    }

def calculate_spacing(parent, child, default_padding=0):
    """
    Calculates spacing between a parent and a child node.
    Now includes calculations for all four sides.
    """
    parent_x = parent.get('x', 0)
    parent_y = parent.get('y', 0)
    parent_width = parent.get('width', 0)
    parent_height = parent.get('height', 0)
    child_x = child.get('x', 0)
    child_y = child.get('y', 0)
    child_width = child.get('width', 0)
    child_height = child.get('height', 0)

    # Use parent’s padding if set, otherwise default_padding.
    parent_padding_left = parent.get('paddingLeft', default_padding) or default_padding
    parent_padding_top = parent.get('paddingTop', default_padding) or default_padding
    parent_padding_right = parent.get('paddingRight', default_padding) or default_padding
    parent_padding_bottom = parent.get('paddingBottom', default_padding) or default_padding

    # Auto layout margin calculation (normalized relative to parent's padded origin)
    auto_layout_margin_left = child_x - (parent_x + parent_padding_left)
    auto_layout_margin_left = max(auto_layout_margin_left, 0)  # Ensure non-negative
    auto_layout_margin_top = child_y - (parent_y + parent_padding_top)
    auto_layout_margin_top = max(auto_layout_margin_top, 0)  # Ensure non-negative
    auto_layout_margin_right = (parent_x + parent_width - parent_padding_right) - (child_x + child_width)
    auto_layout_margin_right = max(auto_layout_margin_right, 0)  # Ensure non-negative
    auto_layout_margin_bottom = (parent_y + parent_height - parent_padding_bottom) - (child_y + child_height)
    auto_layout_margin_bottom = max(auto_layout_margin_bottom, 0)  # Ensure non-negative
    
    return {
        'child_name': child.get('name', 'Unnamed'),
        'auto_layout_based': {
            'parent_padding': {
                'left': parent_padding_left,
                'top': parent_padding_top,
                'right': parent_padding_right,
                'bottom': parent_padding_bottom
            },
            'margin': {
                'left': auto_layout_margin_left,
                'top': auto_layout_margin_top,
                'right': auto_layout_margin_right,
                'bottom': auto_layout_margin_bottom
            }
        }
    }

def process_json_file(filename, default_padding=0):
    # Load JSON file
    with open(filename, 'r') as f:
        figma_data = json.load(f)
    
    # Extract nodes recursively, starting from the document node.
    document = list(figma_data["nodes"].values())[0]["document"]
    nodes = extract_nodes(document)
    
    # Group nodes by their parent
    parent_to_children = defaultdict(list)
    for node in nodes:
        if node.get('parent') is not None:
            parent_to_children[node['parent']['name']].append(node)
    
    results = []
    # Calculate spacing for each parent-child relationship
    for parent_name, children in parent_to_children.items():
        # Find the parent node
        parent_node = next(node for node in nodes if node.get('name') == parent_name)
        
        # Calculate the parent's padding based on all children
        parent_padding = calculate_parent_padding(parent_node, children)
        
        # Update the parent's padding in the node
        parent_node.update(parent_padding)
        
        # Calculate spacing for each child
        for child in children:
            spacing = calculate_spacing(parent_node, child, default_padding)
            results.append(spacing)
    
    return results


def simplify_node(node, parent=None, default_padding=0):
    """
    Returns a simplified version of the node with its geometry data.
    """
    if 'size' not in node:
        return None
    return {
        'name': node.get('name', 'Unnamed'),
        'x': node['size'].get('x', 0),
        'y': node['size'].get('y', 0),
        'width': node['size'].get('width', 0),
        'height': node['size'].get('height', 0),
        'paddingLeft': node.get('paddingLeft', default_padding),
        'paddingTop': node.get('paddingTop', default_padding),
        'paddingRight': node.get('paddingRight', default_padding),
        'paddingBottom': node.get('paddingBottom', default_padding),
        'parent': parent  # simplified parent, if available
    }

def print_tree(node, default_padding=0, indent=0):
    """
    Recursively prints a tree of nodes. For each node that has children,
    we first compute its padding (based on its children) and then print the child margins.
    """
    simplified = simplify_node(node, default_padding=default_padding)
    if simplified is None:
        return

    indent_str = ' ' * indent
    print(f"{indent_str}Node: {simplified['name']}")
    # If the node has children, process them:
    if 'children' in node and isinstance(node['children'], list) and node['children']:
        # Extract only the children with a "size" property (valid nodes)
        valid_children = [child for child in node['children'] if 'size' in child]
        if valid_children:
            # Simplify children
            simplified_children = [
                simplify_node(child, parent=simplified, default_padding=default_padding)
                for child in valid_children
            ]
            # Calculate parent's padding from its children
            parent_padding = calculate_parent_padding(simplified, simplified_children)
            # Update our simplified node for use in margin calculation.
            simplified.update(parent_padding)
            print(f"{indent_str}  Padding: {parent_padding}")
            
            # For each child, calculate and print spacing relative to the parent.
            for child, child_simplified in zip(valid_children, simplified_children):
                spacing = calculate_spacing(simplified, child_simplified, default_padding)
                print(f"{indent_str}  Child: {child_simplified['name'][:10]}")
                #print(f"{indent_str}    Strict Margin: {spacing['strict_margin']}")
                print(f"{indent_str}    Auto Layout Margin: {spacing['auto_layout_based']['margin']}")
                # Recurse on the child's own subtree
                print_tree(child, default_padding, indent + 4)
                

if __name__ == '__main__':
    import json
    # Replace with your actual JSON file path
    filename = 'test/data.json'
    with open(filename, 'r') as f:
        figma_data = json.load(f)
    # Assuming the file structure is similar to Figma’s where we have a document
    document = list(figma_data["nodes"].values())[0]["document"]

    # Print the hierarchical tree with margins and paddings.
    print_tree(document, default_padding=20)
    print("\n\n\n")
