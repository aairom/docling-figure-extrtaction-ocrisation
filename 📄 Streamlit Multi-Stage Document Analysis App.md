# 📄 Streamlit Multi-Stage Document Analysis App

This repository contains a containerized Streamlit application designed for a multi-stage document analysis workflow. It allows users to upload a PDF, extract figures/tables (Stage 1: Document Processing), and then submit those extracted items to a Large Vision Model (LVM) running on Ollama for descriptive analysis (Stage 2: Vision Model Processing).

## 🚀 Setup and Launch

This application is designed to be run entirely using Docker Compose, which manages both the Streamlit web application and the Ollama API server.

### Prerequisites

You must have **Docker** and **Docker Compose** installed on your system.

### 1. File Structure

Ensure you have the following files in the root directory:

```
.
├── app.py              # The Streamlit application logic (GUI)
├── Dockerfile          # Defines the environment for the Streamlit app
├── docker-compose.yaml # Orchestrates the Ollama and Streamlit services
└── requirements.txt    # Python dependencies (at least streamlit and requests)
```

### 2. Prepare the Ollama Model

Before starting the entire stack, you must ensure the Vision Model is available in the Ollama container.

1. **Start the Ollama service:**

   ```
   docker compose up -d ollama
   ```

2. **Pull the Model:** Once the Ollama container is running (it may take a moment), pull the necessary vision model.

   - *Note: `granite3.2-vision` is used as a placeholder in `app.py`. Replace it with your actual desired VLM.*

   ```
   docker compose exec ollama ollama pull granite3.2-vision
   ```

3. **Stop the Ollama service (optional but recommended):**

   ```
   docker compose stop ollama
   ```

### 3. Launch the Application

Start both services and build the Streamlit image:

```
docker compose up --build
```

### 4. Access the UI

Open your web browser and navigate to the following URL:

```
http://localhost:8501
```

## 🛠️ Components

### `app.py` (Streamlit Application)

This file contains the Streamlit code that creates the user interface.

- It handles **PDF uploads**.
- It currently **MOCKS** the document processing (figure extraction) to focus on the full containerized flow. In a production environment, this is where a tool like Docling would run.
- It displays the "extracted" figures (mocked placeholders).
- It sends a request to the **Ollama** service to analyze a specific figure using the VLM.

### `Dockerfile` (Streamlit Environment)

This defines the environment for the `app` service. It installs the Python dependencies from `requirements.txt` and runs the Streamlit application using the correct port configuration.

### `docker-compose.yaml` (Orchestration)

This file orchestrates the two main services:

| **Service**  | **Image/Build**               | **Port Mapping** | **Purpose**                                                  |
| ------------ | ----------------------------- | ---------------- | ------------------------------------------------------------ |
| **`ollama`** | `ollama/ollama:latest`        | `11434:11434`    | Provides the VLM API endpoint. Data is persisted via a volume (`ollama_data`). |
| **`app`**    | Built from local `Dockerfile` | `8501:8501`      | Runs the Streamlit web application. Depends on `ollama` and connects to it using the service name `ollama`. |

The use of `depends_on: ollama` ensures the Streamlit application waits for the Ollama service to start up, minimizing connection errors.