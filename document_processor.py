import logging
import time
import os
from pathlib import Path
from datetime import datetime

# NOTE: The 'docling' imports are assumed to be available in the execution environment,
# as they were used in the original script.
try:
    # UPDATED: Added PictureItem and TableItem to imports
    from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
except ImportError:
    # Fallback/stub for environments where docling might not be installed,
    # but the logic remains sound based on the original request.
    print("Warning: docling library not found. The script structure is provided based on the original app, but it requires docling to run.")
    class DummyDocumentConverter:
        def convert(self, path):
            raise NotImplementedError("Docling not available.")
    DocumentConverter = DummyDocumentConverter
    class ImageRefMode:
        EMBEDDED = 'embedded'
    class InputFormat:
        PDF = 'pdf'
    class PdfPipelineOptions:
        pass
    class PdfFormatOption:
        def __init__(self, pipeline_options):
            pass
    # ADDED: Stubs for PictureItem and TableItem
    class PictureItem: pass
    class TableItem: pass


_log = logging.getLogger(__name__)

# --- Configuration ---
INPUT_DIR = Path("./input")
OUTPUT_DIR = Path("./output")
# NEW: Define separate directory for figure exports
OUTPUT_FIGURES_DIR = Path("./output_figures")
IMAGE_RESOLUTION_SCALE = 2.0  # Higher scale for better image quality if exported

def setup_directories():
    """Ensures input and output directories exist."""
    _log.info(f"Checking input directory: {INPUT_DIR}")
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    _log.info(f"Checking output directory: {OUTPUT_DIR}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # NEW: Create the figures output directory
    _log.info(f"Checking figures output directory: {OUTPUT_FIGURES_DIR}")
    OUTPUT_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def get_input_files():
    """Recursively finds all files in the input directory."""
    # We will primarily target PDF files as per the original script's focus.
    files = list(INPUT_DIR.rglob("*.pdf"))
    if not files:
        _log.warning(f"No PDF files found in '{INPUT_DIR}' or its subfolders. Please place documents here.")
    return files

def process_document(input_file: Path, doc_converter: DocumentConverter):
    """
    Processes a single document file, generating timestamped JSON, Markdown, and exported figures/tables.
    """
    start_time = time.time()
    current_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_stem = input_file.stem.replace(' ', '_')

    # Construct the required timestamped prefix for the output filename
    output_prefix = f"{doc_stem}_{current_time_str}"
    
    output_json_path = OUTPUT_DIR / f"{output_prefix}.json"
    output_md_path = OUTPUT_DIR / f"{output_prefix}.md"

    _log.info(f"-> Processing file: {input_file.name}")

    try:
        # 1. Convert the document
        conv_res = doc_converter.convert(input_file)
        document = conv_res.document

        # 2. Save output as JSON
        document.save_as_json(output_json_path)
        _log.info(f"   - Saved JSON output to: {output_json_path}")

        # 3. Export individual figure/table images
        table_counter = 0
        picture_counter = 0
        
        _log.info("   - Exporting individual figures and tables...")
        for element, _level in document.iterate_items():
            if isinstance(element, TableItem):
                table_counter += 1
                # Use the new OUTPUT_FIGURES_DIR for tables
                element_image_filename = (
                    OUTPUT_FIGURES_DIR / f"{output_prefix}-table-{table_counter}.png"
                )
                with element_image_filename.open("wb") as fp:
                    # element.get_image(document) gets the PIL Image object
                    element.get_image(document).save(fp, "PNG")
                
            if isinstance(element, PictureItem):
                picture_counter += 1
                # Use the new OUTPUT_FIGURES_DIR for pictures/figures
                element_image_filename = (
                    OUTPUT_FIGURES_DIR / f"{output_prefix}-figure-{picture_counter}.png"
                )
                with element_image_filename.open("wb") as fp:
                    element.get_image(document).save(fp, "PNG")

        _log.info(f"   - Exported {picture_counter} figures and {table_counter} tables to {OUTPUT_FIGURES_DIR}.")

        # 4. Save output as Markdown
        document.save_as_markdown(output_md_path, image_mode=ImageRefMode.EMBEDDED)
        _log.info(f"   - Saved Markdown output to: {output_md_path}")

    except Exception as e:
        _log.error(f"   - Failed to process {input_file.name}: {e}")
        return

    end_time = time.time() - start_time
    _log.info(f"-> Finished processing {input_file.name} in {end_time:.2f} seconds.")


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 1. Setup Directories
    setup_directories()
    
    # 2. Configure Docling Converter
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    # Keep page and picture images so they can be embedded in the Markdown output
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    # 3. Get Files and Process
    input_files = get_input_files()
    
    if not input_files:
        _log.info("No documents to process. Application finished.")
        return

    total_start_time = time.time()
    
    _log.info(f"Starting processing of {len(input_files)} document(s)...")

    for input_file in input_files:
        process_document(input_file, doc_converter)

    total_end_time = time.time() - total_start_time
    _log.info(f"All documents processed in a total of {total_end_time:.2f} seconds.")


if __name__ == "__main__":
    main()
