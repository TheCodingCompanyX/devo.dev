import base64, openai
from utils import encode_image
import os
import time
# from playwright.sync_api import sync_playwright

client = openai.Client()


# #This function is now NOT used
# def take_screenshot(url, output_path, device):
#     """Take a screenshot of the specified URL."""
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()
#         try:
#             page.goto(url, timeout=60000)  # Wait up to 60 seconds for the page to load
#             page.wait_for_load_state("networkidle")  # Wait for the page to fully load
#             # Optional: Check for the selector if it's necessary
#             # if not page.query_selector("main"):
#             #     print("'main' selector not found. Proceeding with the screenshot.")
#             # #Rename old screenshot based on timestamp old name is screenshot.png
#             # Rename old screenshot based on timestamp if it exists
#             if os.path.exists(output_path):
#                 timestamp = time.strftime("%Y%m%d-%H%M%S")
#                 os.rename(output_path, f"{output_path}-{timestamp}.png")

#             if device == "mobile":
#                 page.set_viewport_size({"width": 375, "height": 812})
#             elif device == "tablet":
#                 page.set_viewport_size({"width": 1024, "height": 1366})
#             else:
#                 page.set_viewport_size({"width": 1920, "height": 1080})
#             page.screenshot(path=output_path, full_page=True)
#             print(f"Screenshot saved to {output_path}")
#         except Exception as e:
#             print(f"An error occurred: {e}")
#         finally:
#             browser.close()


#This function is now NOT used
def get_ui_feedback(screenshot_path, design_image_path):
    """Use GPT-4 Vision to analyze the UI and provide feedback."""
    try:
        path = "../samplereactproject/app/playground"
        files = os.listdir(path)
        for file in files:
          if os.path.isdir(f"{path}/{file}"):
              continue
          if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg"):
              continue
          with open(f"{path}/{file}", "r") as f:
              code += f"{file}\n```\n"
              code += f.read()
              code += "\n```\n"
        response = client.chat.completions.create(
        model="gpt-4", 
        messages=[
            {"role": "user", 
             "content":  [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(design_image_path)}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(screenshot_path)}"}},
                {"type": "text", "text": "Given the ideal design (1) and the code's output(2). Which UI elements in the code's output do not match the design?"}
            ]},
        ],
        )
        intermediate_result = response.choices[0].message.content
        print(intermediate_result)
        return intermediate_result
        
    except Exception as e:
        #logging.error(f"Error getting UI feedback: {e}")
        raise

def get_design_feedback(figma_data, image_path, route):
    """Use GPT-4 to provide feedback on the design."""
    #base64_image = encode_image(image_path)

    try:
        
        files = os.listdir(route)
        code = ""
        for file in files:
          if os.path.isdir(f"{route}/{file}"):
              continue
          if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg"):
              continue
          with open(f"{route}/{file}", "r") as f:
              code += f"{file}\n```\n"
              code += f.read()
              code += "\n```\n"

        formatted_str = ", ".join(f"{key}: {value}" if isinstance(value, int) else f"{key}: {value}" for key, value in figma_data.items())
        cleaned_figma_string = formatted_str.replace(",", "").replace("'", "").replace(".0", "")
        full_prompt = f"""Design reference:\n{cleaned_figma_string}\n\nCode:\n{code}\nThe given design data has the measurements and styles of the responsive UI components that need to be built.\nThe measurements have X, Y, Height and Width. These should NOT be used as-is. Based on the measurements, use your judgment to check the margins, paddings, height, width and alignment are correct and that the component is responsive.\nList only major issues with the code, such as stylings and spacing. Highlight issues precisely, do not suggest code changes."""
        print(full_prompt)
        response = client.chat.completions.create(
        model="o1-mini", 
        messages=[
            {"role": "user", 
             "content":  [
                {"type": "text", "text": full_prompt}
            ]},
        ]
        )

        result = response.choices[0].message.content
        print(result)
        return result.replace("**", "")
        
    except Exception as e:
        print(f"Error getting UI feedback: {e}")
        raise

def test_UI(figma_data, base_dir, route):
    """Test the UI generated by the code."""
    return get_design_feedback(figma_data, base_dir, route)


import json

if __name__ == "__main__":
    with open('cleaned_figma_data.json', 'r') as f:
        figma_data = json.loads(f.read())
    test_UI(figma_data=figma_data, base_dir="../samplereactproject/app/playground", route="../samplereactproject/app/playground")