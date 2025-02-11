
from utils import encode_image 
from openai import OpenAI
client = OpenAI()
import os
from file_parser import parse_chatgpt_output

initial_prompt = """
You are writing code for a Next.js project with Tailwinds Css.
The filepaths of the icons/pictures to use have been provided, use them. 
The styling information is also given. Use it.
You will output the file contents for the components necessary to achive the user goal. 

Represent the component files like so:

FILENAME
```
CODE
```

The following tokens must be replaced like so:
FILENAME is the lowercase combined path and file name including the file extension
CODE is the code in the file

Example representation of a file:

page.js
```
export default function Page() {
    return <div>page is the parent component</div>;
    }
```

Do not comment on what every file does.
Please note that the code should be fully functional. No placeholders.
Make sure to name the parent component's filename as `page.js`.
Use Next.js and Tailwinds to create responsive components for the given design.
Note: The size of the elements given is not to be used as is. It is just given for you to make judgement. Use your own judgement for the creating responsive and flexible components.
"""

incorporate_feedback = """
You will be given feedback on the output of the code you have written and the ideal design. You will output the MODIFIED content of the files which need to be updated to FIX the issues given, including ALL code.

Represent files like so:

FILENAME    
```
CODE
```

Example representation of a file:

page.js
```
export default function Page() {
    return <div>page is the parent component</div>;
    }
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


# Example usage
chat_output = """
file:\n\n./app/playground/page.js\n```javascript\n"use client";\n\nimport { useState } from 'react';\n\nexport default function Page() {...}```
"""

chat_output = """

**playground/page.js**
```javascript
import AddCard from './AddCard';
import CardDetails from './CardDetails';
import ActionButtons from './ActionButtons';

export default function Page() {
  return (
    <div className="bg-black min-h-screen flex flex-col items-center space-y-6 py-6">
      <AddCard />
      <CardDetails />
      <ActionButtons />
    </div>
  );
}
```

**playground/addcard.js**
```javascript
export default function AddCard() {
  return (
    <div className="flex justify-between items-center bg-gray-900 text-white px-6 py-4 rounded-full">
      <span>Add Your New Card 👉</span>
      <button className="bg-gray-800 rounded-full p-2">
        <span className="text-xl">+</span>
      </button>
    </div>
  );
}
```

**playground/carddetails.js**
```javascript
export default function CardDetails() {
  return (
    <div className="bg-yellow-300 text-black rounded-xl p-6 shadow-lg text-left">
      <div className="font-bold text-xl mb-2">VISA</div>
      <div className="flex justify-between items-center mb-4">
        <span>**** **** **** 3241</span>
        <button>
          <span role="img" aria-label="icon">👁️</span>
        </button>
      </div>
      <div className="text-lg mb-1">Total Balance</div>
      <div className="text-3xl font-bold">$214,453.00</div>
    </div>
  );
}
```

**playground/actionbuttons.js**
```javascript
export default function ActionButtons() {
  const buttons = [
    { name: 'Transfer', icon: '🤝' },
    { name: 'Request', icon: '📬' },
    { name: 'Savings', icon: '💰' },
    { name: 'Contact', icon: '📞' },
  ];

  return (
    <div className="flex justify-around w-full max-w-md">
      {buttons.map((button) => (
        <div key={button.name} className="flex flex-col items-center">
          <button className="bg-gray-800 rounded-full p-4 mb-2">
            <span role="img" aria-label={button.name}>{button.icon}</span>
          </button>
          <span className="text-white">{button.name}</span>
        </div>
      ))}
    </div>
  );
}
```

Ensure you have Tailwind CSS installed and configured in your Next.js project to use these components effectively.
"""

if __name__ == "__main__":
  parse_chatgpt_output(chat_output)