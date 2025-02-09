
from utils import encode_image 
from openai import OpenAI
client = OpenAI()
import os
teststring = 'page.js\n```jsx\nimport React from \'react\';\nimport \'./styles.css\';\n\nexport default function Page() {\n  return (\n    <div className="bg-gray-100 h-screen flex justify-center items-center">\n      <div className="bg-white shadow-md rounded-lg p-8 max-w-md w-full">\n        <div className="bg-coffee-pattern h-24 w-full rounded-t-lg"></div>\n        <h1 className="text-3xl font-bold text-center mt-6">Welcome back!</h1>\n        <p className="text-center text-gray-600 mb-8">Login to your account.</p>\n        <form>\n          <div className="mb-4">\n            <label className="block text-gray-700">Username</label>\n            <input\n              type="text"\n              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-coffee focus:ring-coffee"\n            />\n          </div>\n          <div className="mb-4">\n            <label className="block text-gray-700">Phone Number</label>\n            <input\n              type="text"\n              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-coffee focus:ring-coffee"\n            />\n          </div>\n          <button className="w-full py-2 mt-6 bg-gradient-to-r from-orange-400 to-orange-700 text-white rounded-md hover:from-orange-500 hover:to-orange-800 focus:outline-none focus:ring-2 focus:ring-coffee focus:ring-opacity-50">\n            Login\n          </button>\n        </form>\n      </div>\n    </div>\n  );\n}\n```\n\nstyles.css\n```css\n.bg-coffee-pattern {\n  background-image: url(\'coffee-pattern.png\');\n  background-size: cover;\n  border-bottom-left-radius: 0.5rem;\n  border-bottom-right-radius: 0.5rem;\n}\n\n.focus\\:border-coffee {\n  border-color: #d39b68;\n}\n\n.focus\\:ring-coffee {\n  box-shadow: 0 0 0 0.2rem rgba(211, 155, 104, 0.25);\n}\n```\n\nYou would need to include the `coffee-pattern.png` image in your public folder or adjust the path in the `styles.css` accordingly.'
base_dir = "../samplereactproject/app/playground"
from check_errors import fetch_nextjs_error 
from folder_structure import generate_folder_structure
from file_parser import parse_chatgpt_output
global figma_url
import time

initial_code = """
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

fix_errors = """
You will output the full content of the files which need to be updated to fix the errors.
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
Do not comment on what every file does. Please note that the code should be fully functional. No placeholders.
"""

    
def create_prompt(feedback, error, figma_data):
    code = ""
    if error:
        #Open code files from path
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
        folder_structure = generate_folder_structure("../samplereactproject/app/playground")
        return f"{fix_errors}\n\n{folder_structure}\n\n{code}\n\n{error}"
    if feedback:
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
        return f"{incorporate_feedback}\n\n{code}\n\n{feedback}"
    else:   
        path = "../samplereactproject/app/playground"
        files = os.listdir(path)
        for file in files:
          if os.path.isdir(f"{path}/{file}"):
              continue
          code += f"./{file} "
        formatted_str = ", ".join(f"{key}: {value}" if isinstance(value, int) else f"{key}: {value}" for key, value in figma_data.items())
        cleaned_figma_string = formatted_str.replace(",", "").replace("'", "")
        if code == "":
          return f"Style Info: {cleaned_figma_string}\n\nAssets to use: None\n\n{initial_code}"
        return f"Style Info: {cleaned_figma_string}\n\nAssets to use: {code}\n\n{initial_code}"

def generate_code(image_path, figma_data, feedback, error, chat_history):
    final_prompt = create_prompt(feedback, error, figma_data)
    message = []
    base64_image = encode_image(image_path)
    if feedback: #There is feedback
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
    elif error:
        message = [
            {"role": "user", "content":  [
                {"type": "text", "text": final_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(image_path)}"}},
            ]},
        ]
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

def write_code(image_path, figma_data, feedback, error, URL, chat_history):
    """Generate React code based on the provided prompt and image."""
    code = generate_code(image_path, figma_data, feedback, error, chat_history)
    parse_chatgpt_output(code)
    time.sleep(5)
    error = fetch_nextjs_error(URL)  
    while error:
        print("Errors found in the UI. Would you like me to fix it?")
        print(error)
        #Wait for user input
        user_input = input("Enter 'y' to fix the errors: ")
        if user_input.lower() != 'y':
            time.sleep(5)
            continue
        #logging.info("Errors found in the UI. Generating new code.")
        code = generate_code(image_path, {}, "", error, [])
        parse_chatgpt_output(code)
        error = fetch_nextjs_error(URL)
    return code

#parse_chatgpt_output(teststring)

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