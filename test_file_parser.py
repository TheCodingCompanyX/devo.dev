from file_parser import parse_chatgpt_output

def test_parse_chatgpt_output():
    # Test Case 1: Single File with Long Path
    input1 = """
    app/playground/long/path/to/file.js
    ```javascript
    console.log("Single file test");
    ```
    """
    expected1 = {
        "long/path/to/file.js": 'console.log("Single file test");'
    }

    # Test Case 2: Multiple Files with a Common Prefix
    input2 = """
    app/playground/file1.js
    ```javascript
    console.log("File 1");
    ```

    app/playground/file2.js
    ```javascript
    console.log("File 2");
    ```
    """
    expected2 = {
        "file1.js": 'console.log("File 1");',
        "file2.js": 'console.log("File 2");'
    }

    # Test Case 3: No Common Prefix
    input3 = """
    dir1/file1.js
    ```javascript
    console.log("File 1");
    ```

    dir2/file2.js
    ```javascript
    console.log("File 2");
    ```
    """
    expected3 = {
        "dir1/file1.js": 'console.log("File 1");',
        "dir2/file2.js": 'console.log("File 2");'
    }

    # Test Case 4: Single File with No Path
    input4 = """
    file.js
    ```javascript
    console.log("No path test");
    ```
    """
    expected4 = {
        "file.js": 'console.log("No path test");'
    }

    # Test Case 5: Nested Directories without Prefix
    input5 = """
    playground/nested/directory/file1.js
    ```javascript
    console.log("Nested directory test");
    ```

    playground/nested/directory/file2.js
    ```javascript
    console.log("Another nested test");
    ```
    """
    expected5 = {
        "nested/directory/file1.js": 'console.log("Nested directory test");',
        "nested/directory/file2.js": 'console.log("Another nested test");'
    }

    # Test Case 6: Mixed paths and ignored sections
    input6 = """
    ### dependencies
    ```json
    {
      "dependencies": {
        "react-icons": "^4.10.1",
        "tailwindcss": "^3.3.0"
      }
    }
    ```

    file1.js
    ```javascript
    console.log("File 1");
    ```

    ### run
    ```
    npm install react-icons tailwindcss
    ```
    """
    expected6 = {"file1.js": 'console.log("File 1");'}


    # Test Runner
    inputs = [input1, input2, input3, input4, input5, input6]
    expected_outputs = [expected1, expected2, expected3, expected4, expected5, expected6]

    for i, (input_case, expected) in enumerate(zip(inputs, expected_outputs), start=1):
        print(f"Running Test Case {i}...")
        result = parse_chatgpt_output(input_case)
        # Normalize paths for comparison
        normalized_result = {key.strip(): value.strip() for key, value in result.items()}
        assert normalized_result == expected, f"Test Case {i} Failed: {normalized_result} != {expected}"
        print(f"Test Case {i} Passed!")

# Run the test cases
if __name__ == "__main__":
    test_parse_chatgpt_output()


