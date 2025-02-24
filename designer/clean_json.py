import json


def shorten_keys(json_data):
    if isinstance(json_data, dict):
        keys_to_replace = {
            "fills": "fillColor",
            "strokes": "strokeColor",
            "background": "backgroundColor"
        }
        for key, value in list(json_data.items()):  # Use `list` to avoid runtime errors during iteration
            # Replace "fills", "strokes", and "background" if they match the pattern
            if key in keys_to_replace and isinstance(value, list) and len(value) == 1 and "color" in value[0]:
                json_data[keys_to_replace[key]] = value[0]["color"]
                del json_data[key]  # Remove the original key
            else:
                shorten_keys(value)
    elif isinstance(json_data, list):
        for item in json_data:
            shorten_keys(item)
    
    return json_data

def round_floats(data):
    """Round all floating-point numbers to 0 decimal places."""
    if isinstance(data, dict):
        return {key: round_floats(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [round_floats(item) for item in data]
    elif isinstance(data, float):
        return round(data, 0)
    else:
        return data
    
def merge_singles(data):
    # Remove dictionaries with a single key-value pair and replace with the value
    if isinstance(data, dict):
       
        if len(data.values()) == 1:
            return merge_singles(next(iter(data.values())))
        else:
            return {key: merge_singles(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [merge_singles(item) for item in data]
    else:
        return data

def rgba_to_hex(color):
    """Convert RGBA color dictionary to HEX format."""
    r = int(color['r'] * 255)
    g = int(color['g'] * 255)
    b = int(color['b'] * 255)
    a = int(color['a'] * 255)
    if color['a'] == 1 or color['a'] == 0:
        return f"#{r:02X}{g:02X}{b:02X}"
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"

def replace_color_with_hex(data):
    """Recursively replace color objects with their HEX representation."""
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if (key == "color" or key=="backgroundColor") and isinstance(value, dict):
                try:
                    # Replace the 'color' object with the hex code
                    new_data[key] = rgba_to_hex(value)
                except KeyError:
                    # Skip if the 'color' object is incomplete
                    #(f"Incomplete color object found: {value}")
                    continue
            else:
                new_data[key] = replace_color_with_hex(value)
        return new_data

    elif isinstance(data, list):
        # Process each item in the list
        return [replace_color_with_hex(item) for item in data]

    else:
        # Return scalar values as is
        return data
    
def remove_key_value_pairs(data, config):
    keys_to_remove = config.get("keys_to_remove", [])
    key_value_pairs_to_remove = config.get("key_value_pairs_to_remove", [])

    if isinstance(data, dict):
        cleaned_data = {}
        for key, value in data.items():
            # Check if the key is in the keys_to_remove list
            if key in keys_to_remove:
                #print(f"Removing key: {key}")
                continue
            
            if any({key: value} == pair for pair in key_value_pairs_to_remove):
                #print(f"Removing key-value pair: {key}: {value}")
                continue
            
            # Recursively clean nested structures
            cleaned_data[key] = remove_key_value_pairs(value, config)
        return cleaned_data

    elif isinstance(data, list):
        # Process each item in the list
        return [remove_key_value_pairs(item, config) for item in data]

    else:
        # Return scalar values as is
        return data

def remove_children_by_ids(json_data, target_ids):
    """
    Recursively removes children from nodes with specified IDs in a JSON structure.
    
    Args:
        json_data (dict/list): The JSON data structure to process
        target_ids (list): List of IDs whose children should be removed
        
    Returns:
        The modified JSON structure with children removed from specified nodes
    """
    if isinstance(json_data, dict):
        # If current node's ID is in target_ids, remove 'children'
        if 'id' in json_data and json_data['id'] in target_ids:
            #print(f"Removing children for node: {json_data['id']}")
            return {key: value for key, value in json_data.items() if key != 'children'}
        
        # Otherwise, process children recursively
        return {key: remove_children_by_ids(value, target_ids) for key, value in json_data.items()}
    
    elif isinstance(json_data, list):
        # Process each item in the list
        return [remove_children_by_ids(item, target_ids) for item in json_data]
    
    # Return primitive values as is
    return json_data

def move_children_to_last(json_data):
    """
    Recursively moves the 'children' key to the last position in each node's dictionary.

    Args:
        json_data (dict/list): The JSON data structure to process

    Returns:
        The modified JSON structure with 'children' moved to the last position
    """
    if isinstance(json_data, dict):
        # If 'children' key exists, move it to the last position
        if 'children' in json_data:
            children = json_data.pop('children')
            json_data['children'] = children

        # Process children recursively
        return {key: move_children_to_last(value) for key, value in json_data.items()}

    elif isinstance(json_data, list):
        # Process each item in the list
        return [move_children_to_last(item) for item in json_data]

    # Return primitive values as is
    return json_data

def round_numbers(data):
    # If the data is a dictionary, process each key-value pair recursively.
    if isinstance(data, dict):
        return {key: round_numbers(value) for key, value in data.items()}
    # If it's a list, process each item.
    elif isinstance(data, list):
        return [round_numbers(item) for item in data]
    # If it's a float, check if it represents an integer.
    elif isinstance(data, float):
        # Convert to int if the float is an integer (e.g., 20.0 -> 20)
        if data.is_integer():
            return int(data)
        else:
            # Otherwise, round it normally (you can adjust the rounding precision as needed)
            return round(data)
    # Otherwise, leave the data unchanged.
    else:
        return data

def replace_keys(json_data, key_mapping):
    """
    Recursively replaces keys in a JSON structure based on a mapping.
    
    Args:
        json_data (dict/list): The JSON data structure to process
        key_mapping (dict): A dictionary mapping old keys to new keys
        
    Returns:
        The modified JSON structure with keys replaced based on the mapping
    """
    if isinstance(json_data, dict):
        # Replace keys based on the mapping
        return {key_mapping.get(key, key): replace_keys(value, key_mapping) for key, value in json_data.items()}
    
    elif isinstance(json_data, list):
        # Process each item in the list
        return [replace_keys(item, key_mapping) for item in json_data]
    
    # Return primitive values as is
    return json_data
    
def process_json(data, config):
    """Process the JSON data."""
    #Remove useless key-value pairs
    cleaned_data = remove_key_value_pairs(data, config)
    #Reduce the JSON structure for colors
    cleaned_data = replace_color_with_hex(cleaned_data)
    #Remove children from nodes with specified IDs
    cleaned_data = round_floats(cleaned_data)
    #Shorten keys like fill and then color to fillColor
    cleaned_data = shorten_keys(cleaned_data)   
    #Replace absoluteBoundingBox with size for easier understanding for AI
    cleaned_data = replace_keys(cleaned_data, {"absoluteBoundingBox": "size"})
    #Remove children from nodes with specified IDs so that the AI can focus on the main node one by one
    cleaned_data = move_children_to_last(cleaned_data)
    #round numbers to 0 decimal places
    cleaned_data = round_numbers(cleaned_data)
    return cleaned_data


if __name__ == "__main__":
    figma_url = "https://www.figma.com/design/11ZXUkb3k0dVKWlPswUKZg/Car-Rent-Website-Design---Pickolab-Studio-(Community)?node-id=44-16200&t=25dHcVNVuMpKaWSr-4"
    
    from figma_apis import parse_figma_url, fetch_figma_data, download_and_save_images
    
    file_key, node_id = parse_figma_url(figma_url)
    figma_data = fetch_figma_data(file_key, node_id)

    with open('figma_data.json', 'w') as f:
        f.write(json.dumps(figma_data, indent=4))
    
    node_ids_of_images = download_and_save_images('./test', figma_url)

    #Convert - to :  in node_ids_of_images
    node_ids_of_images = [node_id.replace("-", ":") for node_id in node_ids_of_images]  
    processed_json = remove_children_by_ids(figma_data, node_ids_of_images)
    
    from config_for_spacing import config

    processed_json = process_json(processed_json, config)

    # Save the cleaned JSON data
    with open("designer/test_data/cleaned_figma_data.json", "w") as cleaned_json_file:
        json.dump(processed_json, cleaned_json_file, indent=2)
    