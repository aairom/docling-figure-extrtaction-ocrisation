# Document and Figure Processing Pipeline

This project consists of two linked Python applications designed to automate the extraction of structured data from PDF documents and subsequently perform OCR (Optical Character Recognition) on the extracted figures and tables using local Ollama vision models.

## ⚙️ Setup and Installation

### 1. Python Environment

It is highly recommended to use a virtual environment (`venv`) for dependency management.

```
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows (Command Prompt):
# venv\Scripts\activate.bat
# On Windows (PowerShell):
# venv\Scripts\Activate.ps1
```

### 2. Python Dependencies

The pipeline requires `docling` for PDF processing, `opencv-python` for image handling, and the `ollama` client for the vision models.

```
# Install required libraries
# Note: docling often requires Pillow, which is included here for completeness,
# along with opencv-python to prevent runtime errors like 'No module named cv2'.
pip install docling-core docling opencv-python pillow ollama
```

### 3. Ollama Server (For OCR Processing)

The second stage of the pipeline (`ollama_ocr_processor.py`) requires the [Ollama server] running locally.

1. **Install Ollama:** Download and install the Ollama application for your operating system from the official website.

2. **Run Ollama:** Ensure the Ollama server is running in the background.

3. **Download Models:** Pull the required vision models specified in `ollama_ocr_processor.py`:

   ```
   ollama pull granite3.2-vision
   ollama pull llama3.2-vision
   ```

## 📂 Project Structure

After running the pipeline, the following directory structure will be created and populated:

```
.
├── input/                  # 👈 Place original PDF files here
├── output/                 # 👈 Structured JSON and full Markdown documents
├── output_figures/         # 👈 Extracted figure/table PNG images (Input for Stage 2)
├── figures_results/        # 👈 OCR results (JSON & Markdown reports) from Ollama models
├── document_processor.py   # Stage 1: PDF to Figures/Structured Data
└── ollama_ocr_processor.py # Stage 2: Figure OCR and Reporting
└── README.md
```

## 🚀 Stage 1: Document Processing (`document_processor.py`)

This script handles the initial conversion and data extraction from PDF files.

### Features

- Recursively scans the `./input` directory for `.pdf` files.
- Uses the `docling` library with OCR and image generation enabled.
- Saves full document structure (text, elements, metadata) to timestamped JSON (`./output`).
- Saves full document content to timestamped Markdown (`./output`).
- **Exports all detected figures and tables** as separate timestamped PNG images to the **`./output_figures`** directory.

### How to Run

```
python document_processor.py
```

## 🤖 Stage 2: Ollama OCR Processing (`ollama_ocr_processor.py`)

This script performs Visual Language Model (VLM) OCR on the exported figure images.

### Features

- Recursively scans the **`./output_figures`** directory for images.
- Processes each image using the specified Ollama vision models (`granite3.2-vision` and `llama3.2-vision`).
- Extracts text content from the image (OCR).
- Saves the extracted text, model name, and processing time to timestamped JSON and Markdown report files in the **`./figures_results`** directory. The output file names are prefixed with the original image file name for traceability.

### How to Run

**Prerequisite:** Ensure the Ollama server is running and the necessary models are downloaded (see Setup section).

```
python ollama_ocr_processor.py
```