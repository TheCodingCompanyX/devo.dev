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
    
def clean_json(data):
    # Remove dictionaries with a single key-value pair and replace with the value
    if isinstance(data, dict):
       
        if len(data.values()) == 1:
            return clean_json(next(iter(data.values())))
        else:
            return {key: clean_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_json(item) for item in data]
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
    cleaned_data = remove_key_value_pairs(data, config)
    cleaned_data = replace_color_with_hex(cleaned_data)
    cleaned_data = round_floats(cleaned_data)
    cleaned_data = shorten_keys(cleaned_data)   
    cleaned_data = replace_keys(cleaned_data, {"absoluteBoundingBox": "size"})
    cleaned_data = move_children_to_last(cleaned_data)
    return cleaned_data


if __name__ == "__main__":
    figma_url = "https://www.figma.com/design/Q1nZ4assLAHsrKaHlBf5Po/Untitled?node-id=4-79&t=lfRV7L5YpT1WEhOn-0"
    figma_url = "https://www.figma.com/design/Q1nZ4assLAHsrKaHlBf5Po/Untitled?node-id=4-33&t=O7tq2a5w21t3SRwh-0"
    from figma_apis import parse_figma_url, fetch_figma_data

    try:
        file_key, node_id = parse_figma_url(figma_url)
        print(f"File Key: {file_key}, Node ID: {node_id}")  
        
        # Fetch data from Figma API
        figma_data = fetch_figma_data(file_key, node_id)
        print("Figma Data Retrieved")

        with open('figma_data.json', 'w') as f:
            f.write(json.dumps(figma_data, indent=4))
        
       

    except Exception as e:
        print(f"Error: {e}")


    # Load the JSON data
    with open("figma_data.json", "r") as json_file:
        data = json.load(json_file)

        
    # Load the configuration
    with open("config_for_sizing.json", "r") as config_file:
        config = json.load(config_file) 

    # Process the JSON data
    cleaned_data = process_json(data, config)

    # Save the cleaned JSON data
    with open("cleaned_figma_data.json", "w") as cleaned_json_file:
        json.dump(cleaned_data, cleaned_json_file, indent=2)
    
    formatted_str = ", ".join(f"{key}: {value}" if isinstance(value, int) else f"{key}: {value}" 
                          for key, value in cleaned_data.items())
    
    print(formatted_str.replace(",", "").replace("'", ""))
