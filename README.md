# Color-Detection-from-Images

A simple web app to detect colors from an uploaded image by clicking on it.

## Features
- Upload an image (PNG/JPG/JPEG).
- Click anywhere on the image to read the pixel color.
- Shows:
  - RGB values and Hex.
  - Closest color name from `colors.csv`.
  - Color preview boxes.

## Files
- `app.py` — Streamlit app.
- `colors.csv` — color name dataset (name, hex, R, G, B).
- `requirements.txt` — Python dependencies.

## Setup (local)
1. Clone repository.
2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\Scripts\activate      # Windows
