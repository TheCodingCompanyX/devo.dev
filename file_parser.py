import os
import re

from files_dict import FilesDict

base_dir = "../samplereactproject/app/playground"  # Ensure this is your actual base directory

def parse_chatgpt_output(chat: str) -> FilesDict:
    """
    Converts a chat string containing file paths and code blocks into a FilesDict object.
    Ensures all files are created in the playground folder.

    Args:
    - chat (str): The chat string containing file paths and code blocks.

    Returns:
    - FilesDict: A dictionary with standardized file paths as keys and code blocks as values.
    """

    # Regex to match file paths and associated code blocks
    regex = r"(\S+)\n\s*```[^\n]*\n(.+?)```"
    matches = list(re.finditer(regex, chat, re.DOTALL))

    if not matches:
        return FilesDict()  # No matches found

    # Detect common prefix only if there are multiple matches
    if len(matches) > 1:
        common_prefix = os.path.commonprefix([match.group(1) for match in matches])
        if common_prefix.endswith("/"):
            common_prefix = common_prefix.rstrip("/")  # Remove trailing slash if present
    else:
        common_prefix = ""  # No common prefix if there's only one file

    # Files dictionary to store paths and contents
    files_dict = FilesDict()
    for match in matches:
        # Extract and standardize the file path
        raw_path = match.group(1)
        path = re.sub(r'[\:<>"|?*]', "", raw_path)  # Remove invalid characters
        path = re.sub(r"^\[(.*)\]$", r"\1", path)  # Remove surrounding brackets
        path = re.sub(r"^`(.*)`$", r"\1", path)    # Remove surrounding backticks

        if path.startswith("app/playground/"):
            path = path[len("app/playground/"):]
        elif path.startswith("playground/"):
            path = path[len("playground/"):]

        
        # Extract and clean the code content
        content = match.group(2)

        # Add the standardized path and content to the FilesDict
        files_dict[path.strip()] = content.strip()

    # Write the files to the playground directory
    for file_path, file_content in files_dict.items():
        # Ensure the path is within the playground directory
        full_path = os.path.join(base_dir, file_path)
        folder_path = os.path.dirname(full_path)

        # Create folder structure if necessary
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Write the file content
        with open(full_path, "w", encoding="utf-8") as file:
            file.write(file_content)
        print(f"Created or updated file: {full_path}")

    return files_dict