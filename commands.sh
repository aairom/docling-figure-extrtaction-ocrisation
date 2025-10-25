ollama run llama3.2-vision
ollama run granite3.2-vision
ollama run qwen3-vl:235b-cloud

pip install -r requirements.txt

#### Streamlit version
docker build -t streamlit_app .
#docker run -p 8501:8501 --name my_standalone_app streamlit_app

docker run -p 8501:8501 --name my_standalone_app streamlit_app \
  streamlit run Document-VLM-Processing.py