import re
import requests
import os
import json
from PIL import Image
from io import BytesIO

# Constants
FIGMA_API_BASE_URL = "https://api.figma.com/v1"
figma_token = os.getenv("FIGMA_TOKEN")
print(figma_token)

# Function to parse Figma URL
def parse_figma_url(figma_url):
    pattern = r"https:\/\/www\.figma\.com\/design\/(?P<file_key>[a-zA-Z0-9]+)(?:\/[^?]*)?(?:\?.*?node-id=(?P<node_id>[a-zA-Z0-9:\-]+))?"
    match = re.search(pattern, figma_url)
    if not match:
        raise ValueError("Invalid Figma URL")
    
    file_key = match.group("file_key")
    node_id = match.group("node_id")
    return file_key, node_id

# Function to make API calls
def fetch_figma_data(file_key, node_id=None):
    headers = {
        "X-FIGMA-TOKEN": figma_token
    }
    
    if node_id:
        endpoint = f"{FIGMA_API_BASE_URL}/files/{file_key}/nodes"
        params = {"ids": node_id}
    else:
        endpoint = f"{FIGMA_API_BASE_URL}/files/{file_key}"
        params = {}
    
    response = requests.get(endpoint, headers=headers, params=params)

    
    return response.json()

def fetch_figma_image(file_key, node_id):
    """
    Fetches an image of a specific node from Figma.
    
    Args:
    - file_key (str): The Figma file key.
    - node_id (str): The node ID of the object to export.
    
    Returns:
    - bytes: The image data in bytes.
    
    Raises:
    - Exception: If the API request fails or returns an error.
    """
    headers = {
        "X-FIGMA-TOKEN": figma_token
    }
    
    # Figma Image Export API endpoint
    endpoint = f"{FIGMA_API_BASE_URL}/images/{file_key}?ids={node_id}"
    
    # Send the request to the Figma API
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    
    # Get the image URL from the response
    image_data = response.json()

    image_url = image_data['images'][node_id.replace("-", ":")]


    #print(f"Image URL: {image_url}")
    
    # Download the image from the URL
    img_response = requests.get(image_url)

    
    if img_response.status_code != 200:
        raise Exception(f"Error downloading image: {img_response.status_code}")
    
    # Return the image data in bytes
    return img_response.content


def download_and_save_images(basedir, figma_url):
    file_key, node_id = parse_figma_url(figma_url)
    image_data = fetch_image_ids_from_node(file_key, node_id) 
    """
    Downloads and saves all images from the provided image data.

    Args:
    - image_data (dict): Dictionary of image IDs and their corresponding image URLs.
    - format (str): The image format to save (e.g., png, jpeg, svg).
        """
    node_ids = []
    for image_id, value in image_data.items():
        image_name = value['name']  # Extract the image name
        image_url = value['image_url']  # Extract the image URL
        print(f"Downloading image: {image_name} from {image_url}")
        
        # Send the request to get the image URL
        headers = {
            "X-FIGMA-TOKEN": figma_token
        }
        img_response = requests.get(image_url, headers=headers)
        
        if img_response.status_code != 200:
            print(f"Failed to download image {image_id} (status code: {img_response.status_code})")
            continue
        
        image = Image.open(BytesIO(img_response.content))
        print(image.format)
        format = image.format.lower()
        
        # Get the image content (either SVG or binary)
        if format == "svg":
            image_content = img_response.text
            file_extension = "svg"
        else:
            image_content = img_response.content
            file_extension = format

        # Create the directory if it doesn't exist
        if not os.path.exists(basedir):
            os.makedirs(basedir)
            
        # Save the image locally
        with open(f"{basedir}/{image_name}.{file_extension}", "wb" if format != "svg" else "w") as img_file:
            img_file.write(image_content)
            print(f"Saved image {image_name}.{file_extension} to {basedir}")
            node_ids.append(image_id.replace(":", "-")) 

    return node_ids
           

def fetch_image_ids_from_node(file_key, node_id, format="png", scale=2):
    """
    Fetches all image elements (bitmaps and vectors) of a specific node from Figma.

    Args:
    - file_key (str): The Figma file key.
    - node_id (str): The node ID of the object to export.
    - format (str): The image format to download. Default is "png". Can be "jpeg", "svg", etc.

    Returns:
    - dict: A dictionary of image ids and their corresponding image data.
    """
    headers = {
        "X-FIGMA-TOKEN": figma_token
    }

    # Figma Node API endpoint to retrieve detailed node structure
    endpoint = f"{FIGMA_API_BASE_URL}/files/{file_key}/nodes"
    params = {"ids": node_id}

    response = requests.get(endpoint, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    
    data = response.json()
    node = data['nodes'][node_id.replace("-",":")]

    image_data = {}

    def extract_images_from_node(node, format):
        """Extract image URLs from all layers and elements in a node."""
        all_children_are_vectors = False
        if 'type' in node:
            if node['type'] == 'RECTANGLE' and 'fills' in node:
                print(f"Node: {node['name']}")
                # Check if the element has an image fill (bitmap)
                for fill in node['fills']:
                    if fill.get('type') == 'IMAGE':
                        image_id = node['id']
                        image_url = f"{FIGMA_API_BASE_URL}/images/{file_key}?ids={image_id}&format={format}&scale=2"
                        response = requests.get(image_url, headers=headers)
                        if response.status_code != 200:
                            raise Exception(f"Error: {response.status_code}, {response.text}")
                        image_url = response.json()['images'][image_id]
                        image_data[image_id] = { 'name': node['name'], 'image_url': image_url };
            
            #if node['type'] == 'BOOLEAN_OPERATION' or node['type'] == 'FRAME' or node['type'] == 'GROUP':
            #check if node has children
            if 'children' in node:
                # Check if all the children are vectors
                all_children_are_vectors = all(child['type'] == 'VECTOR' for child in node['children'])
                if all_children_are_vectors:
                    image_url = f"{FIGMA_API_BASE_URL}/images/{file_key}?ids={node['id']}&format=svg"
                    
                    #make a GET request
                    response = requests.get(image_url, headers=headers)
                    # Get the image URL from the response
                    response_result = response.json()
                    image_url = response_result['images'][node['id'].replace("-", ":")]
                    if image_url is None:
                        print(f"Image URL is None for node {node['id']}")
                        return
                    print(f"Image URL: {image_url}")    
                    image_data[node['id']] = { 'name': node['name'], 'image_url': image_url };


                    if response.status_code != 200:
                        raise Exception(f"Error: {response.status_code}, {response.text}")
                    
                # print(f"Node: {node['name']}")
                # print(f"Node ID: {node['id']}")
                # print(f"Node Type: {node['type']}")
                    
        if not all_children_are_vectors:
            if 'document' in node:
                # If the node is a document, extract images from its children
                for child in node['document']['children']:
                    extract_images_from_node(child, format)

            if 'children' in node:
                for child in node['children']:
                    extract_images_from_node(child, format)

    # Recursively extract images from the node's children (sub-elements)
    extract_images_from_node(node, format)

    return image_data

# Main execution
if __name__ == "__main__":
    figma_url = "https://www.figma.com/design/QzCWHjcaXXWZyEquCGKJlg/Untitled?node-id=33-20&t=SNAofFOFUMtNT7KZ-0"

    try:
        file_key, node_id = parse_figma_url(figma_url)
        print(f"File Key: {file_key}, Node ID: {node_id}")  
        
        # Fetch data from Figma API
        figma_data = fetch_figma_data(file_key, node_id)
        print("Figma Data Retrieved")

        with open('figma_data.json', 'w') as f:
            f.write(json.dumps(figma_data, indent=4))
        
        #image_data = fetch_figma_image(file_key, node_id)
        
        # # Save the image locally
        # with open("reference/reference.png", "wb") as img_file:
        #     img_file.write(image_data)

        
        # Download and save all images
        download_and_save_images(basedir=".", figma_url=figma_url)  # Change format as needed
       

    except Exception as e:
        print(f"Error: {e}")

