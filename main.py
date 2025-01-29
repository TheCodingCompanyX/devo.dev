import requests
from openai import OpenAI
from write_code import write_code
#from test_UI import test_UI
from check_errors import fetch_nextjs_error
import os, time, json
from figma_apis import parse_figma_url, fetch_figma_data, fetch_figma_image, download_and_save_images
from clean_json import process_json

global figma_url

route = "playground"
base_dir = "../samplereactproject/app/"+route
figma_url = "https://www.figma.com/design/Q1nZ4assLAHsrKaHlBf5Po/Untitled?node-id=0-20&t=wHSBS2TN2SoOiLyh-0"
device = "web"
client = OpenAI()

# Constants
MAX_ITERATIONS = 20
URL = "http://localhost:3000/"+route

global chat_history

# Main workflow
if __name__ == "__main__":
    chat_history = []

    file_key, node_id = parse_figma_url(figma_url)
    figma_data = fetch_figma_data(file_key, node_id)

    with open('figma_data.json', 'w') as f:
        f.write(json.dumps(figma_data, indent=4))
        
    if os.path.exists('reference/reference.png'):
        os.rename('reference/reference.png', 'reference/reference.png'+str(time.time())+'.png')
    with open('reference/reference.png', 'wb') as img_file:
        img_file.write(fetch_figma_image(file_key, node_id))
    
    #wait for user input
    print("Press y to download images")
    #if input() == "y":
    download_and_save_images("../test", figma_url)

    #feedback = with file open feedback.txt, read the contents
    with open('feedback.txt', 'r') as f:
        feedback = f.read()
        if feedback.strip() == "":
            feedback = ""
        else:
            #wait for user input
            print("Feedback has been found, press y to use it")
            if input() != "y":
                feedback = ""
            else:
                with open('feedback.txt', 'r') as f:
                    feedback = f.read()

    for iteration in range(MAX_ITERATIONS):
        print("Press Enter to write code")
        input()
        
        code = write_code("./reference/reference.png", process_json(figma_data), feedback, "", URL, [])
        
        #feedback = test_UI(URL, SCREENSHOT_PATH, device=device)
        with open('feedback.txt', 'w') as f:
            f.write(feedback)
        
        if feedback=="":
            break