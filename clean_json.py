import json

def round_floats(data):
    """Round all floating-point numbers to 2 decimal places."""
    if isinstance(data, dict):
        return {key: round_floats(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [round_floats(item) for item in data]
    elif isinstance(data, float):
        return round(data, 2)
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

# Load the configuration
with open("config.json", "r") as config_file:
    config = json.load(config_file) 


    
def process_json(data):
    """Process the JSON data."""
    cleaned_data = replace_color_with_hex(data)
    cleaned_data = remove_key_value_pairs(cleaned_data, config)
    cleaned_data = round_floats(cleaned_data)
    return cleaned_data


if __name__ == "__main__":
    # Load the JSON data
    with open("figma_data.json", "r") as json_file:
        data = json.load(json_file)

    # Process the JSON data
    cleaned_data = process_json(data)

    # Save the cleaned JSON data
    with open("cleaned_figma_data.json", "w") as cleaned_json_file:
        json.dump(cleaned_data, cleaned_json_file, indent=4)