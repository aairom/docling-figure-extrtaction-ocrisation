import streamlit as st
import requests
import base64
import time
import json
from io import BytesIO

# --- Configuration ---
# In a Docker Compose network, services can talk to each other using their service names.
# The Ollama service is named 'ollama' in the docker-compose.yaml file.
OLLAMA_BASE_URL = "http://ollama:11434/api" 
MODEL_NAME = "granite3.2-vision" # Or any other VLM like llava, bakllava, etc.

# --- Helper Functions (Mocking the Pipeline) ---

@st.cache_data
def mock_docling_extraction(uploaded_file):
    """
    Mocks the functionality of the docling 'document_processor' (Stage 1).
    In a real app, this would use docling to process the PDF and export 
    the text and figure images.
    """
    st.info(f"Simulating PDF processing for: {uploaded_file.name}. This is where docling runs.")
    
    time.sleep(1.5) # Simulate processing time

    # Mock Extracted Text Content
    text_content = (
        "The primary finding of this study confirms the effectiveness of the proposed "
        "model (Figure 1). Data preprocessing steps, as detailed in Section 3.1, "
        "involved scaling and normalization. The experimental results, showing an 87% "
        "accuracy rate (Table 1), surpassed previous benchmarks. Future work will focus "
        "on integrating multi-modal inputs, leveraging the figure analysis provided below."
    )

    # Mock Extracted Figures (using placeholder images)
    # The image data is created on the fly for demonstration.
    mock_figures = [
        {"id": "Figure 1", "prompt": "Identify the primary relationship shown in this scatter plot and summarize the finding."},
        {"id": "Table 1", "prompt": "Extract the accuracy rate from the table."},
    ]
    
    # Generate placeholder images for demonstration
    for fig in mock_figures:
        url = f"https://placehold.co/400x300/1e293b/f1f5f9?text={fig['id']}"
        response = requests.get(url)
        fig['image_data'] = response.content
    
    return text_content, mock_figures

def call_ollama_vlm(image_data, prompt, model_name):
    """
    Communicates with the Ollama service to perform VLM analysis (Stage 2).
    """
    st.info(f"Contacting Ollama VLM (Model: {model_name}) for analysis...")
    
    # 1. Convert image to base64
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    # 2. Construct the Ollama API payload
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "images": [base64_image]
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        # 3. Call the Ollama API endpoint for generation
        response = requests.post(f"{OLLAMA_BASE_URL}/generate", 
                                 headers=headers, 
                                 data=json.dumps(payload),
                                 timeout=60)
        
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        
        result = response.json()
        return result.get('response', 'VLM response was empty.')

    except requests.exceptions.ConnectionError:
        st.error(f"Connection Error: Could not connect to Ollama at {OLLAMA_BASE_URL}. "
                 f"Ensure the 'ollama' container is running and the '{model_name}' model is pulled.")
        return "ERROR: Could not connect to the VLM server."
    except requests.exceptions.RequestException as e:
        st.error(f"Ollama Request Error: {e}")
        return f"ERROR: VLM request failed ({e})."


# --- Streamlit UI ---

def main():
    st.set_page_config(
        page_title="Containerized Document Pipeline (Docling + Ollama VLM)",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🤖 AI-Powered Document Analyzer")
    st.markdown("---")

    # --- Sidebar Configuration (VLM Setup) ---
    with st.sidebar:
        st.header("VLM Configuration")
        vlm_model = st.text_input("Ollama VLM Model:", value=MODEL_NAME)
        st.caption("E.g., `llava`, `bakllava`, or `granite3.2-vision`. Must be pulled in the Ollama container.")
        
        st.markdown("---")
        st.subheader("Pipeline Overview")
        st.markdown("""
            1. **Upload PDF:** File is uploaded.
            2. **Docling (Mocked):** Extracts main text, tables, and figures.
            3. **Ollama VLM:** Extracted figures are analyzed by the VLM for OCR/captioning.
            4. **Results:** Display organized text and VLM outputs.
        """)

    # --- Main Application Area (Stage 1: Document Processing) ---
    st.header("Step 1: Upload Document & Extract Content")
    uploaded_file = st.file_uploader("Upload a PDF Document", type="pdf")

    if uploaded_file:
        if st.button("Start Full Pipeline Analysis"):
            
            # --- Document Processor (Stage 1) ---
            with st.spinner("Processing PDF and extracting figures..."):
                extracted_text, extracted_figures = mock_docling_extraction(uploaded_file)
            
            st.success("Document structure extracted successfully.")
            
            st.subheader("Extracted Document Text")
            st.code(extracted_text, language='markdown')

            # --- Ollama OCR Processor (Stage 2) ---
            st.header("Step 2: Figure/Table VLM Analysis")
            st.markdown(f"Sending **{len(extracted_figures)}** figures to the **{vlm_model}** VLM for specialized analysis.")

            figure_results = []
            
            # Use a progress bar for the VLM calls
            vlm_progress = st.progress(0)
            
            for i, figure in enumerate(extracted_figures):
                st.subheader(f"Analyzing {figure['id']}")
                
                # Call the VLM
                response = call_ollama_vlm(figure['image_data'], figure['prompt'], vlm_model)
                
                # Display the figure and the VLM result side-by-side
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(figure['image_data'], caption=figure['id'], use_column_width=True)
                
                with col2:
                    st.markdown("**VLM Prompt:**")
                    st.write(figure['prompt'])
                    st.markdown("**VLM Analysis/OCR Result:**")
                    st.info(response)

                vlm_progress.progress((i + 1) / len(extracted_figures))
                figure_results.append({"id": figure['id'], "response": response})

            st.balloons()
            st.success("🎉 Full Pipeline Analysis Complete!")


if __name__ == "__main__":
    main()
