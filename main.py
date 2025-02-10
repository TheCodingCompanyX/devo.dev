from openai import OpenAI
from write_code import write_code
import os, json
from figma_apis import parse_figma_url, fetch_figma_data, fetch_figma_image, download_and_save_images
from clean_json import process_json, remove_children_by_ids
from test_UI import test_UI

global figma_url

route = "playground"
base_dir = "../samplereactproject/app/"+route

with open("figma_url.txt", "r") as f:
    figma_url = f.read().strip()

if figma_url == "":
    figma_url = input("Enter Figma URL: ")
else:
    print("Figma URL found in figma_url.txt: " + figma_url)
    print("Press y to use this URL, press any other key to enter a new URL")
    if input() != "y":
        figma_url = input("Enter New Figma URL: ")
        with open("figma_url.txt", "w") as f:
            f.write(figma_url)

client = OpenAI()

URL = "http://localhost:3000/"+route


# Main workflow
if __name__ == "__main__":
    #chat_history = []

    file_key, node_id = parse_figma_url(figma_url)
    figma_data = fetch_figma_data(file_key, node_id)

    with open('figma_data.json', 'w') as f:
        f.write(json.dumps(figma_data, indent=4))
        
    with open('reference.png', 'wb') as img_file:
        img_file.write(fetch_figma_image(file_key, node_id))

    print("Reference image saved at './reference.png\n\n")
    
    #wait for user input
    print("Press y to download images")
    if input() == "y":
        node_ids_of_images = download_and_save_images("../samplereactproject/app/playground", figma_url)

    #print paths of images
    print("Images have been downloaded")

    # Load the configuration
    with open("config_initial.json", "r") as config_file:
        config = json.load(config_file) 

    #Convert - to :  in node_ids_of_images
    node_ids_of_images = [node_id.replace("-", ":") for node_id in node_ids_of_images]  
    processed_json = remove_children_by_ids(figma_data, node_ids_of_images)
    processed_json = process_json(processed_json, config)

    # Save the cleaned JSON data
    with open("cleaned_figma_data.json", "w") as cleaned_json_file:
        json.dump(processed_json, cleaned_json_file, indent=2)

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

    for iteration in range(20):

        print("Press Enter to write code")
        input()
        
        code = write_code("./reference.png", processed_json, feedback, "", URL, [])
        
        #Another Debug Point Here

        print("Code written successfully\n\n")

        print("Press Y to test UI, press any other key to skip testing")
        if input().lower == "y":
            feedback = test_UI(processed_json, base_dir)
            with open('feedback.txt', 'w') as f:
                f.write(feedback)
            print("Check feedback.txt for feedback. You can edit the feedback now\n\n")

        print("Press enter to continue, press q to quit")
        if input() == "q":
            break

        with open('feedback.txt', 'r') as f:
            feedback = f.read()
        

        if feedback=="":
            break