#!/bin/bash
# Install Tesseract OCR on Render server
apt-get install -y tesseract-ocr
apt-get install -y tesseract-ocr-hin
apt-get install -y libtesseract-dev

# Install Python dependencies
pip install -r requirements.txt