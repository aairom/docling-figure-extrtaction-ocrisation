#!/bin/sh 
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install docling
pip install opencv-python
pip install ollama