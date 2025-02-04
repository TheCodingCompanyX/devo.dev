import os
from openai import OpenAI

from write_code import write_code
#from test_UI import test_UI
from check_errors import fetch_nextjs_error
import os, time, json
from figma_apis import parse_figma_url, fetch_figma_data, fetch_figma_image, download_and_save_images
from clean_json import process_json, remove_children_by_ids
# from test_UI import test_UI

global figma_url

route = "playground"
base_dir = "../samplereactproject/app/"+route
figma_url = "https://www.figma.com/design/Q1nZ4assLAHsrKaHlBf5Po/Untitled?node-id=4-33&t=lvuG5RBb7Xwv7NNy-0"
device = "web"
client = OpenAI()

# Constants
MAX_ITERATIONS = 20
URL = "http://localhost:3000/"+route

#global chat_history

# Main workflow
if __name__ == "__main__":
    #chat_history = []

    file_key, node_id = parse_figma_url(figma_url)
    figma_data = fetch_figma_data(file_key, node_id)

    with open('figma_data.json', 'w') as f:
        f.write(json.dumps(figma_data, indent=4))
        
    # if os.path.exists('reference.png'):
    #     os.rename('reference.png', 'reference.png'+str(time.time())+'.png')
    with open('reference.png', 'wb') as img_file:
        img_file.write(fetch_figma_image(file_key, node_id))
    
    #wait for user input
    #print("Press y to download images")
    #if input() == "y":
    node_ids_of_images = download_and_save_images("../samplereactproject/app/playground", figma_url)

    # Load the configuration
    with open("config.json", "r") as config_file:
        config = json.load(config_file) 

    #Convert - to :  in node_ids_of_images
    node_ids_of_images = [node_id.replace("-", ":") for node_id in node_ids_of_images]  

    processed_json = remove_children_by_ids(figma_data, node_ids_of_images)
    processed_json = process_json(processed_json, config)

    # Save the cleaned JSON data
    with open("cleaned_figma_data.json", "w") as cleaned_json_file:
        json.dump(processed_json, cleaned_json_file, indent=2)

    #feedback = with file open feedback.txt, read the contents
    with open('feedback.txt', 'r') as f:
        feedback = f.read()
        if feedback.strip() == "":
            feedback = ""
        else:
            #wait for user input
            print("Feedback has been found, press y to use it")
            if input() == "y":
                with open('feedback.txt', 'r') as f:
                    feedback = f.read()
            else:
                feedback = ""

    for iteration in range(MAX_ITERATIONS):
        
        code = write_code("./reference.png", processed_json, feedback, "", URL, [])
        
        #Another Debug Point Here

        # uncomment when needed
        #feedback = test_UI(processed_json, base_dir)
        with open('feedback.txt', 'w') as f:
            f.write(feedback)

        #Add Debug Point Here for feedback editing
        with open('feedback.txt', 'r') as f:
            feedback = f.read()
        

        if feedback=="":
            break