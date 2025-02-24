import requests
import json
import re

def fetch_nextjs_error(base_url):
    """
    Fetches and extracts the most recent error shown on the Next.js server.
    
    Args:
        base_url (str): The URL of the Next.js server (e.g., 'http://localhost:3000').
    """

    # Fetch the HTML page
    response = requests.get(base_url)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        print("Your React app might not be running. Please check your server.")
        print("Press Enter if you have started the server, or type 'exit' to quit.")
        user_input = input()
        if user_input.lower() == 'exit':
            return
        
        else:
            return fetch_nextjs_error(base_url)
        
    html_content = response.text

    # Use regex to extract JSON from the __NEXT_DATA__ script tag
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content, re.DOTALL)
    if match:
        json_data = json.loads(match.group(1))  # Parse the JSON data

        # Check if there's an error in the `err` field
        if "err" in json_data:
            error_data = json_data["err"]

            # Extract and format the error message
            error_message = error_data.get("message", "No error message available.")
            error_stack = error_data.get("stack", "No stack trace available.")

            print("⚠️ Current Error:")
            return(error_message)
            # print("\nStack Trace:")
            # print(error_stack)
        else:
            return("")

    else:
        return("")

if __name__ == "__main__":
    # Define the base URL of your Next.js development server
    BASE_URL = "http://localhost:3000/playground"

    print(f"Fetching the most recent error from {BASE_URL}...")
    fetch_nextjs_error(BASE_URL)
