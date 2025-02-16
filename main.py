from openai import OpenAI
from write_code import write_code
import os, json
from figma_apis import parse_figma_url, fetch_figma_data, fetch_figma_image, download_and_save_images
from clean_json import process_json, remove_children_by_ids
from test_UI import test_UI

global figma_url

base_dir = os.getcwd()
print("Current working directory: " + base_dir)


if not os.path.exists("figma_url.txt"):
    with open("figma_url.txt", "w") as f:
        f.write("")

with open("figma_url.txt", "r") as f:
    figma_url = f.read().strip()

if figma_url == "":
    figma_url = input("Enter Figma URL: ")
    with open("figma_url.txt", "w") as f:
        f.write(figma_url)
else:
    print("Figma URL found in figma_url.txt: " + figma_url)
    print("Press Enter to use this URL or type in the new URL")
    new_url = input()
    if new_url != "":
        figma_url = new_url
        with open("figma_url.txt", "w") as f:
            f.write(figma_url)

client = OpenAI()


if not os.path.exists("rules.txt"):
    with open("rules.txt", "w") as f:
        f.write("")

with open("rules.txt", "r") as f:
    rules = f.read().strip()

    if rules == "":
        print("No rules found, please enter rules in rules.txt")
    else:
        print("Rules found in rules.txt: " + rules)
        print("Press Enter to use these rules") 
        input()

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

    print("Where should devo write the code? Press Enter to use '/app/playground', or enter a new path like '/app/your_folder'")
    route = input()
    if route == "":
        route = "/app/playground"
        #Check if you have write permissions

    if not os.path.exists('./'+route):
        os.makedirs('./'+route)
    
    from config_initial import config
    print("Press Enter to download images, or type any other key to skip")
    if input() == "":
        node_ids_of_images = download_and_save_images('./'+route, figma_url)

        #print paths of images
        print("Images have been downloaded at "+route)
        #Convert - to :  in node_ids_of_images
        node_ids_of_images = [node_id.replace("-", ":") for node_id in node_ids_of_images]  
        processed_json = remove_children_by_ids(figma_data, node_ids_of_images)
        processed_json = process_json(processed_json, config)

    else:
        processed_json = figma_data
        processed_json = process_json(processed_json, config)


    print("Images have been downloaded at "+route)
    print("Please check the images, download images manually if needed")

    if not os.path.exists('feedback.txt'):
        with open('feedback.txt', 'w') as f:
            f.write("")

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

        #Tasks
        #1. Write fresh new code
        #2. Test the code for design issues and generate feedback
        #3. Test the code for functionality and generate feedback
        #4. Do API Integration
        #5. Generate Empty File Structure
        #6. Auto Complete the existing code
        #7. Fix Errors
        #8. Modify existing code to match new design/make it responsive

        print("Press Enter to write code, press any key to skip to testing")
        if input() == "":
            code = write_code("./reference.png", processed_json, feedback, "http://localhost:3000/"+route, [], './'+route)
            print("\n\nCode written successfully\n\n")

        print("Press Enter to test UI, press any other key to skip to editing feedback")
        if input() == "":
            feedback = test_UI(processed_json, base_dir, './'+route)
            with open('feedback.txt', 'w') as f:
                f.write(feedback)
            print("\n\nCheck feedback.txt for feedback. You can edit the feedback now\n\n")

        print("Press enter to continue using given feedback, press q to quit")
        if input() == "q":
            break

        with open('feedback.txt', 'r') as f:
            feedback = f.read()
        

        if feedback=="":
            break