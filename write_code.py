
from utils import encode_image 
from openai import OpenAI
client = OpenAI()
import os
from file_parser import parse_chatgpt_output

framework = 'Next.js'
style_framework = 'Tailwinds Css'

initial_prompt = f"""
You are writing code for a {framework} {style_framework} project.
The filepaths of the icons/pictures to use have been provided, use them. 
The styling information is also given. Use it.
You will output the file contents for the components in the design and import them into ./page.js, the parent component.

Represent the component files like so:

FILENAME
```
CODE
```

The following tokens must be replaced like so:
FILENAME is the lowercase combined path and file name including the file extension
CODE is the code in the file

Example representation of a file:

./page.js
```
export default function Page() {{
    return <div>page is the parent component</div>;
    }}
```

Do not comment on what every file does.
Please note that the code should be fully functional. No placeholders.
Note: The size of the elements given is not to be used as is. It is just given for you to make judgement. Use your own judgement for the creating responsive and flexible components.
"""

incorporate_feedback = f"""
You are editing code in a {framework} {style_framework} project.  You will be given feedback on the code you have written and the ideal design. You will output the MODIFIED content of the files which need to be updated to FIX the issues given, including ALL code.

Represent files like so:

FILENAME    
```
CODE
```

Example representation of a file:

page.js
```
export default function Page() {{
    return <div>page is the parent component</div>;
    }}
```

Please note that the code should be fully functional. No placeholders.
"""

    
def create_prompt(feedback, figma_data, route):
  with open("rules.txt", "r") as f:
      rules = f.read()

  empty_string = ""
  if feedback:
    files = os.listdir(route)
    for file in files:
      if file.startswith("."):
          continue
      if os.path.isdir(f"{route}/{file}"):
          continue
      if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg"):
          continue
      with open(f"{route}/{file}", "r") as f:
          empty_string += f"{file}\n```\n"
          empty_string += f.read()
          empty_string += "\n```\n"
    return f"{incorporate_feedback}\n{rules}\n{empty_string}\n\n{feedback}"
  else:   
    files = os.listdir(route)
    for file in files:
      if file.startswith("."):
          continue
      if os.path.isdir(f"{route}/{file}"):
          continue
      empty_string += f"./{file} "
    formatted_str = ", ".join(f"{key}: {value}" if isinstance(value, int) else f"{key}: {value}" for key, value in figma_data.items())
    cleaned_figma_string = formatted_str.replace(",", "").replace("'", "")
    if empty_string == "":
      return f"Style Info: {cleaned_figma_string}\n{rules}\nAssets to use: None\n\n{initial_prompt}"
    return f"Style Info: {cleaned_figma_string}\n{rules}\nAssets to use: {empty_string}\n\n{initial_prompt}"

def generate_code(image_path, figma_data, feedback, chat_history, route):
  final_prompt = create_prompt(feedback, figma_data, route)
  message = []
  base64_image = encode_image(image_path)
  if feedback: 
    if chat_history:
      if len(chat_history) <3:
        message = chat_history[-2:-1]
      elif len(chat_history) >= 3 and len(chat_history) < 5:
        message = chat_history[-4:-1]
      else:
        message = chat_history[-6:-1]
    else:
        message = []
    message.append({"role": "user", "content":  [
        {"type": "text", "text": final_prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(image_path)}"}},
    ]})
    selected_model = "gpt-4o"
  else :
    message = [
      {"role": "user", "content":  [
          {"type": "text", "text": final_prompt},
          {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
      ]},
    ]
    selected_model = "gpt-4o"
      
  print("Chat History:")
  print(chat_history)
  
  print(final_prompt)
  print(selected_model)
  print("Thinking about code...")

  response = client.chat.completions.create(
    model=selected_model,
    messages=message,
    temperature=0.1,
    top_p=0.9,
  )
  result = response.choices[0].message.content
  print(result)
  return str(result)

def write_code(image_path, figma_data, feedback, URL, chat_history, route):
  """Generate React code based on the provided prompt and image."""
  code = generate_code(image_path, figma_data, feedback, chat_history, route)
  parse_chatgpt_output(code)
  return code
