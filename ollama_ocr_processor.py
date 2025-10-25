import os
import json
import base64
import ollama
import time
from pathlib import Path
from datetime import datetime # Added for timestamping

# --- Configuration ---
# Updated INPUT_DIR to read from where the figures are exported
INPUT_DIR = Path("./output_figures")
# New OUTPUT_DIR for the results
OUTPUT_DIR = Path("./figures_results")

# Simplified MODELS list since the output directory is now fixed
MODELS = [
    {"name": "granite3.2-vision"},
    {"name": "llama3.2-vision"},
    {"name": "qwen3-vl:235b-cloud"},
]

# --- Helper Functions ---
def is_image_file(filename):
    """Checks if a file has a common image extension."""
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
    return Path(filename).suffix.lower() in image_extensions

def get_base64_image(image_path):
    """Reads an image file and returns its Base64-encoded string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except IOError as e:
        print(f"Error reading image file {image_path}: {e}")
        return None

def process_image_with_ollama(model_name, image_path, base64_image):
    """Sends an image to the Ollama model for text extraction."""
    print(f"Processing image with {model_name}: {image_path}")
    start_time = time.time()
    try:
        # Note: Ollama must be running and models must be available
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": "Extract all text from this image.",
                    "images": [base64_image],
                }
            ],
        )
        end_time = time.time()
        extracted_text = response['message']['content']
        elapsed_time = end_time - start_time
        return extracted_text, elapsed_time
    except Exception as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Error with Ollama API for {image_path} using model {model_name}: {e}")
        return None, elapsed_time

def save_to_json(filepath: Path, data):
    """Saves data to a JSON file."""
    try:
        with open(filepath, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Successfully saved JSON to {filepath}")
    except IOError as e:
        print(f"Error writing to JSON file {filepath}: {e}")

def save_to_markdown(filepath: Path, text: str):
    """Saves text to a Markdown file, providing context."""
    try:
        with open(filepath, "w", encoding="utf-8") as md_file:
            md_file.write(f"# OCR Extraction Report\n\n")
            md_file.write(f"## Extracted Text\n\n")
            md_file.write(text)
        print(f"Successfully saved Markdown to {filepath}")
    except IOError as e:
        print(f"Error writing to Markdown file {filepath}: {e}")

# --- Main Application Logic ---
def main():
    """Main function to run the OCR process for multiple models."""
    print("Starting Ollama OCR application...")

    # 1. Setup Directories
    if not INPUT_DIR.exists():
        print(f"Error: The input directory '{INPUT_DIR}' does not exist. Please run the document processor first to generate images.")
        return
        
    # Create the required output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output results will be written to: {OUTPUT_DIR}")


    # 2. Create a list of all image paths to process recursively
    image_paths = []
    # os.walk is used for recursive traversal
    for root, _, files in os.walk(INPUT_DIR):
        for filename in files:
            if is_image_file(filename):
                image_paths.append(Path(root) / filename)

    if not image_paths:
        print(f"No image files found recursively in '{INPUT_DIR}'. Please check the folder contents.")
        return

    # 3. Process images with each model
    for model_info in MODELS:
        model_name = model_info["name"]
        
        print(f"\nProcessing images with model: {model_name}")

        for image_path in image_paths:
            # Get the Base64 representation of the image
            base64_image = get_base64_image(image_path)
            if not base64_image:
                continue  # Skip to the next file if there was an error

            # Process the image with the Ollama model and get the elapsed time
            extracted_text, elapsed_time = process_image_with_ollama(model_name, image_path, base64_image)
            
            # Print the elapsed time for the current image
            print(f"  - Time elapsed for {image_path.name}: {elapsed_time:.2f} seconds.")

            if extracted_text:
                # Generate unique, timestamped, and prefixed filename
                current_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                # Use the stem of the original image file
                image_stem = image_path.stem 
                # Sanitize model name for use in a filename
                sanitized_model_name = model_name.replace(':', '_').replace('-', '_')
                
                # New output format: {image_stem}_{timestamp}_{model_name}
                output_prefix = f"{image_stem}_{current_time_str}_{sanitized_model_name}"
                
                # Define output file paths
                output_json_path = OUTPUT_DIR / f"{output_prefix}.json"
                output_md_path = OUTPUT_DIR / f"{output_prefix}.md"
                
                # Prepare data for JSON file
                json_data = {
                    "original_image_path": str(image_path),
                    "extracted_text": extracted_text,
                    "model_used": model_name,
                    "processing_time_seconds": round(elapsed_time, 2),
                    "timestamp": current_time_str
                }
                
                # Save the extracted data in JSON and Markdown
                save_to_json(output_json_path, json_data)
                save_to_markdown(output_md_path, extracted_text)
            else:
                print(f"Could not extract text from {image_path} with model {model_name}. Skipping.")

    print("\nOllama OCR application finished.")

if __name__ == "__main__":
    main()
