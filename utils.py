import base64

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# def run_eslint_prettier():
#     """Run ESLint and Prettier to validate and format code."""
#     try:
#         subprocess.run(["npx", "eslint", "--fix", "../samplereactproject/app/playground/page.js"], check=True)
#         #logging.info("Code linted and formatted successfully.")
#     except subprocess.CalledProcessError as e:
#         #logging.error(f"ESLint/Prettier error: {e}")
#         raise
