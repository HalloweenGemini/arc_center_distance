from utils_func import *
from pydicom import dcmread
from pydicom.data import get_testdata_file
from pydicom.pixel_data_handlers.util import apply_voi_lut

import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

from PIL import Image, ImageDraw, ImageFont
import cv2

import math

import pandas as pd
from streamlit_drawable_canvas import st_canvas

st.set_page_config(layout="wide")
st.header('Hinge joint sagittal plane view')
dcm = st.file_uploader("X-ray, CT Dicom",
                      help="""
Ankle X-ray를 Upload 하십시오
""")

if "points" not in st.session_state:
    st.session_state["points"] = []

# Define a function to draw on the image
def draw_on_image(image, coordinates):
    # Draw a circle at the coordinates
    radius = 5
    color = "red"
    draw = ImageDraw.Draw(image)
    x, y = coordinates
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)

def get_ellipse_coords(point, radius=3):
    center = point
    radius = 1
    return (
        center[0] - radius,
        center[1] - radius,
        center[0] + radius,
        center[1] + radius,
    )


def define_circle(p1, p2, p3):
    """
    Returns the center and radius of the circle passing the given 3 points.
    In case the 3 points form a line, returns (None, infinity).
    """
    temp = p2[0] * p2[0] + p2[1] * p2[1]
    bc = (p1[0] * p1[0] + p1[1] * p1[1] - temp) / 2
    cd = (temp - p3[0] * p3[0] - p3[1] * p3[1]) / 2
    det = (p1[0] - p2[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p2[1])
    
    if abs(det) < 1.0e-6:
        return (None, np.inf)
    
    # Center of circle
    cx = (bc*(p2[1] - p3[1]) - cd*(p1[1] - p2[1])) / det
    cy = ((p1[0] - p2[0]) * cd - (p2[0] - p3[0]) * bc) / det
    
    radius = np.sqrt((cx - p1[0])**2 + (cy - p1[1])**2)
    return ((cx, cy), radius)

drawing_mode = st.sidebar.selectbox(
    "Drawing tool:",
    ("point", "freedraw", "line", "rect", "circle", "transform", "polygon"),
)

# stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
if drawing_mode == 'point':
    point_display_radius = st.sidebar.slider("Point display radius: ", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color hex: ")
# bg_color = st.sidebar.color_picker("Background color hex: ", "#eee")
# bg_image = st.sidebar.file_uploader("Background image:", type=["png", "jpg"])
# realtime_update = st.sidebar.checkbox("Update in realtime", True)


if dcm is not None : 

    ds = dcmread(dcm)
    coordinates_list = []
    
    if ds.Modality == 'CT' :
        y_ratio, x_ratio = ds.PixelSpacing
    
    else : 
    
        y_ratio, x_ratio = ds.ImagerPixelSpacing

    ds_array= ds.pixel_array

    ds_array = cv2.normalize(ds_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    ds_array = np.dstack([ds_array,ds_array,ds_array])

    cv2.imwrite(os.path.join('ds_array.jpg'), ds_array)
    
    
    # coordinates_list = []
    image = Image.fromarray(ds_array)

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        # stroke_width=stroke_width,
        stroke_color=stroke_color,
        # background_color=bg_color,
        background_image=Image.open('ds_array.jpg'),
        update_streamlit=True,
        height=ds_array.shape[0],
        width =ds_array.shape[1],
        drawing_mode=drawing_mode,
        point_display_radius=point_display_radius if drawing_mode == 'point' else 0,
        display_toolbar=st.sidebar.checkbox("Display toolbar", True),
        key="full_app",
    )
    
    # When the canvas is clicked, append the coordinates to the list
    if canvas_result.image_data is not None:
        # Convert the image data to a numpy array
        

        # Get the coordinates of the drawn circle
        coordinates = np.where(canvas_result.image_data[:,:,3] != 0)
        x, y = int(np.mean(coordinates[1])), int(np.mean(coordinates[0]))
        st.session_state["points"].append((x, y))

        # Draw the circle on the image
        draw_on_image(image, (x, y))

        # Show the image with the drawn circle
        st.image(image, use_column_width=True)

        # Show the coordinates
        st.write(f"Clicked on ({x}, {y})")

    # Show the list of coordinates
    st.write("List of coordinates:")
    st.write(st.session_state["points"])