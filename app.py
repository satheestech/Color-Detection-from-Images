# app.py
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import io
import plotly.express as px
from streamlit_plotly_events import plotly_events
import math

st.set_page_config(page_title="Color Detector", page_icon="🎨", layout="centered")

st.title("🎨 Color Detector")
st.markdown(
    "Upload an image, click anywhere on it, and see the pixel's RGB values, the closest color name, and a color preview."
)

# --- Load color dataset ---
@st.cache_data
def load_colors(csv_path="colors.csv"):
    df = pd.read_csv(csv_path)
    # Expecting csv columns: color_name, hex, R, G, B
    # If hex present but R/G/B missing, compute them
    if "R" not in df.columns or "G" not in df.columns or "B" not in df.columns:
        def hex_to_rgb(h):
            h = h.lstrip("#")
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        rgb_cols = df['hex'].apply(lambda x: pd.Series(hex_to_rgb(x)))
        rgb_cols.columns = ["R", "G", "B"]
        df = pd.concat([df, rgb_cols], axis=1)
    return df

try:
    colors_df = load_colors("colors.csv")
except FileNotFoundError:
    st.error("colors.csv not found. Make sure colors.csv is in the same folder as app.py.")
    st.stop()

# --- Helper: find closest color name ---
def closest_color_name(r, g, b, colors_df):
    # Euclidean distance in RGB space
    distances = ((colors_df["R"] - r) ** 2 + (colors_df["G"] - g) ** 2 + (colors_df["B"] - b) ** 2)
    idx = distances.idxmin()
    row = colors_df.loc[idx]
    return {
        "name": row.get("color_name", row.get("name", "Unknown")),
        "hex": row.get("hex", "#{:02x}{:02x}{:02x}".format(int(row.R), int(row.G), int(row.B))),
        "R": int(row.R),
        "G": int(row.G),
        "B": int(row.B)
    }

# --- Upload image ---
uploaded = st.file_uploader("Upload an image (png/jpg/jpeg)", type=["png", "jpg", "jpeg"])
if not uploaded:
    st.info("Upload an image to begin. You can use the sample image below for testing.")
    if st.button("Load sample image"):
        # small built-in sample: create gradient if no file
        sample = Image.new("RGB", (400, 300))
        for x in range(400):
            for y in range(300):
                sample.putpixel((x,y), (int(255 * x/399), int(255 * y/299), 140))
        uploaded = io.BytesIO()
        sample.save(uploaded, format="PNG")
        uploaded.seek(0)
    else:
        st.stop()

image = Image.open(uploaded).convert("RGB")
img_arr = np.array(image)

# Make a plotly image so we can capture clicks
fig = px.imshow(img_arr)
fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    dragmode=False,
    xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
    yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, autorange="reversed")
)
st.caption("Click on the image to detect a color. (If no click registers, try zooming out or clicking again.)")

# Display interactive plotly and capture click events
clicked = plotly_events(fig, click_event=True, hover_event=False)  # returns list of events

if clicked:
    # plotly returns [{'x': float_x, 'y': float_y, ...}]
    click = clicked[0]
    # x and y correspond to pixel column and row
    x = int(round(click["x"]))
    y = int(round(click["y"]))
    # clamp to bounds
    h, w = img_arr.shape[0], img_arr.shape[1]
    x = max(0, min(w - 1, x))
    y = max(0, min(h - 1, y))
    r, g, b = img_arr[y, x].tolist()  # note: array is (row=y, col=x)
    # compute closest
    closest = closest_color_name(r, g, b, colors_df)

    st.markdown("### Detected Pixel")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write(f"**Coordinates:** (x={x}, y={y})")
        st.write(f"**RGB:** R={r}, G={g}, B={b}")
        hex_val = "#{:02x}{:02x}{:02x}".format(r, g, b)
        st.write(f"**Hex:** {hex_val}")
    with col2:
        st.write("**Closest color from dataset:**")
        st.write(f"**Name:** {closest['name']}")
        st.write(f"**Dataset RGB:** R={closest['R']}, G={closest['G']}, B={closest['B']}")
        st.write(f"**Dataset Hex:** {closest['hex']}")

    st.markdown("**Color preview:**")
    # show two boxes: detected color and dataset match
    preview_html = f"""
    <div style="display:flex;gap:12px;">
      <div style="width:120px;height:80px;background:{hex_val};border:1px solid #000;">
        <div style="font-size:12px;padding:4px;color:#fff;text-shadow:0 0 4px rgba(0,0,0,0.8);">
          Detected
        </div>
      </div>
      <div style="width:120px;height:80px;background:{closest['hex']};border:1px solid #000;">
        <div style="font-size:12px;padding:4px;color:#fff;text-shadow:0 0 4px rgba(0,0,0,0.8);">
          Closest match
        </div>
      </div>
    </div>
    """
    st.components.v1.html(preview_html, height=110)
else:
    st.info("No click detected yet — click somewhere on the image. (If clicking doesn't work, try a different browser or click again.)")
