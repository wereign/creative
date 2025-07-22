import streamlit as st
import numpy as np
import cv2
import tempfile
import os
from PIL import Image

# --- Utility functions ---
def create_negative_mask(width, height, num_slices=300, rect_width=4, rect_height_ratio=0.6, min_spacing=0, max_spacing=0):
    # Accept a list of colors in RGB order
    color_mask = np.zeros((height, width, 3), dtype=np.uint8)
    rect_height = int(height * rect_height_ratio)
    x = 0
    # Use global or closure variable for color list
    global BAR_COLORS
    while x < width:
        y = np.random.randint(0, height - rect_height)
        color_idx = np.random.randint(0, len(BAR_COLORS))
        color_rgb = BAR_COLORS[color_idx]
        color_bgr = (color_rgb[2], color_rgb[1], color_rgb[0])
        cv2.rectangle(color_mask, (x, y), (x + rect_width, y + rect_height), color_bgr, -1)
        if min_spacing == 0 and max_spacing == 0:
            x += rect_width
        else:
            x += rect_width + np.random.randint(min_spacing, max_spacing+1)
    return color_mask

def apply_vertical_streaking(mask, num_slices=300):
    if len(mask.shape) == 2:
        height, width = mask.shape
        result = mask.copy()
        for _ in range(num_slices):
            x = np.random.randint(0, width)
            w = np.random.randint(1, 5)
            y_offset = np.random.randint(-100, 101)
            for y in range(height):
                for dx in range(w):
                    sx = np.clip(x + dx, 0, width - 1)
                    sy = np.clip(y, 0, height - 1)
                    ty = np.clip(y + y_offset, 0, height - 1)
                    result[ty, sx] = mask[sy, sx]
        return result
    else:
        height, width, ch = mask.shape
        result = mask.copy()
        for _ in range(num_slices):
            x = np.random.randint(0, width)
            w = np.random.randint(1, 5)
            y_offset = np.random.randint(-100, 101)
            for y in range(height):
                for dx in range(w):
                    sx = np.clip(x + dx, 0, width - 1)
                    sy = np.clip(y, 0, height - 1)
                    ty = np.clip(y + y_offset, 0, height - 1)
                    result[ty, sx, :] = mask[sy, sx, :]
        return result

def apply_horizontal_slicing(mask, num_slices=150):
    if len(mask.shape) == 2:
        height, width = mask.shape
        result = mask.copy()
        for _ in range(num_slices):
            y = np.random.randint(0, height)
            h = np.random.randint(1, 5)
            x_offset = np.random.randint(-50, 51)
            src_y = np.clip(y, 0, height - h)
            dest_y = src_y
            slice_ = result[src_y : src_y + h, :]
            shifted = np.roll(slice_, shift=x_offset, axis=1)
            result[dest_y : dest_y + h, :] = shifted
        return result
    else:
        height, width, ch = mask.shape
        result = mask.copy()
        for _ in range(num_slices):
            y = np.random.randint(0, height)
            h = np.random.randint(1, 5)
            x_offset = np.random.randint(-50, 51)
            src_y = np.clip(y, 0, height - h)
            dest_y = src_y
            slice_ = result[src_y : src_y + h, :, :]
            shifted = np.roll(slice_, shift=x_offset, axis=1)
            result[dest_y : dest_y + h, :, :] = shifted
        return result

def mask_image(image, bars_img):
    mask_black = np.all(bars_img == 0, axis=2)
    result = image.copy()
    # Use broadcasting to assign colored bars to all channels
    for c in range(3):
        result[..., c][~mask_black] = bars_img[..., c][~mask_black]
    return result

# --- Streamlit UI ---
st.title("Glitch Mask Visualizer")

uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded.read())
    img = cv2.imread(tfile.name)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    height, width = img.shape[:2]


    st.sidebar.header("Bar Parameters")
    num_slices = st.sidebar.slider("Number of Bars", 10, 500, 250)
    rect_width = st.sidebar.slider("Bar Width", 1, 40, 4)
    rect_height_ratio = st.sidebar.slider("Bar Height Ratio", 0.05, 1.0, 0.6, step=0.05)
    min_spacing = st.sidebar.slider("Min Spacing", 0, 100, 8)
    max_spacing = st.sidebar.slider("Max Spacing", min_spacing, 200, 32)

    st.sidebar.header("Bar Colors")
    num_colors = st.sidebar.number_input("Number of Colors", min_value=1, max_value=8, value=2, step=1)
    default_colors = ["#FFC470", "#DD5746", "#FFD700", "#00FF00", "#00BFFF", "#FF69B4", "#8A2BE2", "#FFFFFF"]
    color_pickers = []
    for i in range(num_colors):
        color = st.sidebar.color_picker(f"Color {i+1}", default_colors[i % len(default_colors)])
        # Convert hex to RGB tuple
        color_rgb = tuple(int(color.lstrip('#')[j:j+2], 16) for j in (0, 2, 4))
        color_pickers.append(color_rgb)
    global BAR_COLORS
    BAR_COLORS = color_pickers

    st.sidebar.header("Distortion Parameters")
    num_v = st.sidebar.slider("Vertical Streaks", 0, 500, 300)
    num_h = st.sidebar.slider("Horizontal Slices", 0, 500, 150)

    # Step 1: Bars
    bars_img = create_negative_mask(width, height, num_slices, rect_width, rect_height_ratio, min_spacing, max_spacing)
    bars_img_rgb = cv2.cvtColor(bars_img, cv2.COLOR_BGR2RGB)
    st.subheader("Step 1: Colored Bars")
    st.image(bars_img_rgb)
    step1_result = mask_image(img, bars_img_rgb)
    st.image(step1_result, caption="Step 1: Masked Image")

    # Step 2: Vertical Streaks
    bars_v = apply_vertical_streaking(bars_img, num_v)
    bars_v_rgb = cv2.cvtColor(bars_v, cv2.COLOR_BGR2RGB)
    st.subheader("Step 2: Vertical Streaks")
    st.image(bars_v_rgb)
    step2_result = mask_image(img, bars_v_rgb)
    st.image(step2_result, caption="Step 2: Masked Image")

    # Step 3: Horizontal Slices
    bars_h = apply_horizontal_slicing(bars_v, num_h)
    bars_h_rgb = cv2.cvtColor(bars_h, cv2.COLOR_BGR2RGB)
    st.subheader("Step 3: Horizontal Slices")
    st.image(bars_h_rgb)
    step3_result = mask_image(img, bars_h_rgb)
    st.image(step3_result, caption="Step 3: Masked Image")

    st.success("Adjust the sliders to see changes in real time!")
else:
    st.info("Upload an image to begin.")
