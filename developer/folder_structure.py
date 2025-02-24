import os

#This file generates a texts structure of the folder this can be used by the AI to fix path related errors. We dont use it currently

def generate_folder_structure(root_folder):
    log = []

    def traverse_folder(root_folder, folder, indent_level):
        indent = " " * indent_level

        # Ignore directories starting with "."
        if os.path.basename(folder).startswith('.'):
            return

        log.append(f"{indent}- {folder.split('/')[-1]}")

        for item in os.listdir(folder):
            item_path = os.path.join(folder, item)

            if os.path.isdir(item_path):
                traverse_folder(root_folder, item_path, indent_level + 1)
            else:
                log.append(f"{indent} - {item}")

    root_folder = os.path.join(root_folder)
    traverse_folder(root_folder, root_folder, 0)

    return "\n".join(log)

if __name__ == "__main__":
    print(generate_folder_structure("../samplereactproject"))