import json
from collections import defaultdict

def calculate_spacing(parent, child):
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

   
    # Auto layout margin calculation (normalized relative to parent's padded origin)
    auto_layout_margin_left = child_x - (parent_x)
    auto_layout_margin_left = max(auto_layout_margin_left, 0)  # Ensure non-negative
    auto_layout_margin_top = child_y - (parent_y)
    auto_layout_margin_top = max(auto_layout_margin_top, 0)  # Ensure non-negative
    auto_layout_margin_right = (parent_x + parent_width) - (child_x + child_width)
    auto_layout_margin_right = max(auto_layout_margin_right, 0)  # Ensure non-negative
    auto_layout_margin_bottom = (parent_y + parent_height) - (child_y + child_height)
    auto_layout_margin_bottom = max(auto_layout_margin_bottom, 0)  # Ensure non-negative
    
    return {
        'child_name': child.get('name', 'Unnamed'),
        'auto_layout_based': {
            'space': {
                'left': auto_layout_margin_left,
                'top': auto_layout_margin_top,
                'right': auto_layout_margin_right,
                'bottom': auto_layout_margin_bottom
            }
        }
    }

def compute_individual_margins(parent, children):
    """
    For each child (dictionary with x, y, width, height), compute margins relative to the parent's boundaries.
    Also, adjust each side by checking for overlapping siblings.
    If a computed gap is negative, it is flagged as an overlap.
    
    Returns a list of dictionaries:
    [{
        'child': child_dict,
        'left': {'value': L, 'overlap': True/False},
        'right': {'value': R, 'overlap': True/False},
        'top': {'value': T, 'overlap': True/False},
        'bottom': {'value': B, 'overlap': True/False}
    }, ...]
    """
    results = []
    px = parent['x']
    py = parent['y']
    pw = parent['width']
    ph = parent['height']

    for i, child in enumerate(children):
        cx = child['x']
        cy = child['y']
        cw = child['width']
        ch = child['height']

        # Start with basic margins relative to the parent's boundaries:
        left_margin = cx - px
        right_margin = (px + pw) - (cx + cw)
        top_margin = cy - py
        bottom_margin = (py + ph) - (cy + ch)

        # Flags for overlap (default False)
        left_overlap = False
        right_overlap = False
        top_overlap = False
        bottom_overlap = False

        # Horizontal adjustments (left/right) using siblings overlapping vertically.
        for j, other in enumerate(children):
            
            if i == j:
                continue
            ox = other['x']
            oy = other['y']
            ow = other['width']
            oh = other['height']
            # Check vertical overlap: if not completely separated vertically.
            if not (cy + ch <= oy or cy >= oy + oh):
                # Left side adjustment: sibling is to the left.
                if ox + ow <= cx:
                    gap = cx - (ox + ow)
                    if gap < left_margin:
                        left_margin = gap
                        left_overlap = gap < 0
                # Right side adjustment: sibling is to the right.
                if ox >= cx + cw:
                    gap = ox - (cx + cw)
                    if gap < right_margin:
                        right_margin = gap
                        right_overlap = gap < 0

        # Vertical adjustments (top/bottom) using siblings overlapping horizontally.
        for j, other in enumerate(children):
            if i == j:
                continue
            ox = other['x']
            oy = other['y']
            ow = other['width']
            oh = other['height']
            # Check horizontal overlap: if not completely separated horizontally.
            if not (cx + cw <= ox or cx >= ox + ow):
                # Top side adjustment: sibling is above.
                if oy + oh <= cy:
                    gap = cy - (oy + oh)
                    if gap < top_margin:
                        top_margin = gap
                        top_overlap = gap < 0
                # Bottom side adjustment: sibling is below.
                if oy >= cy + ch:
                    gap = oy - (cy + ch)
                    if gap < bottom_margin:
                        bottom_margin = gap
                        bottom_overlap = gap < 0

        results.append({
            'child': child,
            'left': {'value': left_margin, 'overlap': left_overlap},
            'right': {'value': right_margin, 'overlap': right_overlap},
            'top': {'value': top_margin, 'overlap': top_overlap},
            'bottom': {'value': bottom_margin, 'overlap': bottom_overlap},
        })
    return results

def simplify_node(node, parent=None):
    """
    Returns a simplified version of the node with its geometry data.
    """
    if 'size' not in node:
        return None
    return {
        'id': node.get('id', 'Unnamed'),
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

    """
    Recursively prints a tree of nodes. For each node that has children,
    we first compute its padding (based on its children) and then print the child margins,
    including individual margins with overlap detection.
    """
    simplified = simplify_node(node)
    if simplified is None:
        return

    indent_str = ' ' * indent
    
    # If the node has children, process them:
    if 'children' in node and isinstance(node['children'], list) and node['children']:
        print(f"{indent_str}Node: {simplified['name']}")
        # Extract only the children with a "size" property (valid nodes)
        valid_children = [child for child in node['children'] if 'size' in child]
        if valid_children:
            # Simplify children
            simplified_children = [
                simplify_node(child, parent=simplified)
                for child in valid_children
            ]
            
            child_auto_margins = {}

            for child, child_simplified in zip(valid_children, simplified_children):
                # Calculate auto layout spacing for each child
                spacing = calculate_spacing(simplified, child_simplified)
                #print(f"{indent_str}  Child: {child_simplified['name']}")
                #print(f"{indent_str}    Auto Layout Margin: {spacing['auto_layout_based']['margin']}")

                # Store auto layout margins for this child
                auto_layout_margin = spacing['auto_layout_based']['margin']
                child_auto_margins[child_simplified['name']] = {
                    'left': auto_layout_margin['left'],
                    'right': auto_layout_margin['right'],
                    'top': auto_layout_margin['top'],
                    'bottom': auto_layout_margin['bottom']
                }

            child_margins = compute_individual_margins(simplified, simplified_children)

            for margin in child_margins:
                child_name = margin['child']['name']
                lm = margin['left']
                rm = margin['right']
                tm = margin['top']
                bm = margin['bottom']

                # Retrieve corresponding auto layout margins
                auto_margins = child_auto_margins.get(child_name, {'left': 0, 'right': 0, 'top': 0, 'bottom': 0})

                # Select the minimum of the margins (individual vs auto layout)
                min_left = min(lm['value'], auto_margins['left'])
                min_right = min(rm['value'], auto_margins['right'])
                min_top = min(tm['value'], auto_margins['top'])
                min_bottom = min(bm['value'], auto_margins['bottom'])

                #print(f"{indent_str} {child_name} Left: {lm['value']} Right: {rm['value']} Top: {tm['value']} Bottom: {bm['value']}")
                print(f"{indent_str}   {child_name}   Final margins: min left: {min_left} min right: {min_right} min top: {min_top} min bottom: {min_bottom}")

            # Recurse on the child's own subtree
            for child in valid_children:
                print_tree(child, indent + 4)
                 

def calculate_margins(parent, child):
    return {
        'left': child['x'] - parent['x'],
        'top': child['y'] - parent['y'],
        'right': (parent['x'] + parent['width']) - (child['x'] + child['width']),
        'bottom': (parent['y'] + parent['height']) - (child['y'] + child['height'])
    }

def build_tree(node):
    """
    Recursively prints a tree of nodes. For each node that has children,
    we first compute its padding (based on its children) and then print the child margins,
    including individual margins with overlap detection.
    """
    simplified = simplify_node(node)
    if simplified is None:
        return

    
    # If the node has children, process them:
    if 'children' in node and isinstance(node['children'], list) and node['children']:
        
        # Extract only the children with a "size" property (valid nodes)
        valid_children = [child for child in node['children'] if 'size' in child]
        if valid_children:
            # Simplify children
            simplified_children = [
                simplify_node(child, parent=simplified)
                for child in valid_children
            ]
            # Update our simplified node for use in margin calculation.
            result = {
                'id': simplified['id'],
            }
            
            child_auto_margins = {}

            child_margins = compute_individual_margins(simplified, simplified_children)

            for margin in child_margins:
                child_name = margin['child']['id']
                lm = margin['left']
                rm = margin['right']
                tm = margin['top']
                bm = margin['bottom']

                # Retrieve corresponding auto layout margins
                auto_margins = child_auto_margins.get(child_name, {'left': 0, 'right': 0, 'top': 0, 'bottom': 0})

            
                result = {
                    'id': simplified['id'],
                    'space' : {
                        'left': lm['value'],
                        'right': rm['value'],
                        'top': tm['value'],
                        'bottom': bm['value'],
                    },
                    'children': [build_tree(child) for child in valid_children]
                }

                return result
               
def remove_keys_with_only_name(data):
    if isinstance(data, dict):
        if 'id' in data and len(data) == 1:
            #remove this key-value pair
            return None 
        return {k: remove_keys_with_only_name(v) for k, v in data.items() if remove_keys_with_only_name(v) is not None}
    elif isinstance(data, list):
        return [remove_keys_with_only_name(item) for item in data if remove_keys_with_only_name(item) is not None]
    else:
        return data
    

if __name__ == '__main__':
    filename = './designer/test_data/cleaned_figma_data.json'
    with open(filename, 'r') as f:
        figma_data = json.load(f)
    
    document = list(figma_data["nodes"].values())[0]["document"]
    tree_structure = build_tree(document)

    from clean_json import remove_key_value_pairs

    config = {
        "keys_to_remove": [ 
            "x",
            "y",
            "width",
            "height"
        ],
        "key_value_pairs_to_remove": [
            {"space": {
                        "left": 0,
                        "right": 0,
                        "top": 0,
                        "bottom": 0
                    }},
            {"parent": None},
        ]
    }
        
    tree_structure = remove_key_value_pairs(tree_structure, config)
    
    tree_structure = remove_keys_with_only_name(tree_structure)
    output_filename = './designer/tree_structure.json'
    with open(output_filename, 'w') as f:
        json.dump(tree_structure, f, indent=4)
    
    print(f"Tree structure saved to {output_filename}")

    #Append cleaned figma data with data from tree_structure node by node

    from merge import merge_space_data
    document = list(figma_data["nodes"].values())[0]["document"]

    result = merge_space_data(document,tree_structure)

    from clean_json import move_children_to_last

    result = move_children_to_last(result)

    with open('./designer/test_data/merged_figma_data.json', 'w') as f:
        json.dump(result, f, indent=4)

    

    print("Merged data saved to merged_figma_data.json")
