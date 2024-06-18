from utils_func import *
from pydicom import dcmread
from pydicom.data import get_testdata_file
from pydicom.pixel_data_handlers.util import apply_voi_lut

import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

from PIL import Image, ImageDraw, ImageFont
import cv2

import math

radius10 = 2

st.set_page_config(layout="wide")

drawing_mode = st.sidebar.selectbox(
    "Annotation tool:",
    ("3-point circle", 
     # "Length", 
     # "Cobbs angle",
    ),
)

if "points" not in st.session_state:
    st.session_state["points"] = []


    
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


st.header('Hinge joint sagittal plane view')
dcm = st.file_uploader("X-ray, CT Dicom",
                      help="""
Ankle X-ray를 Upload 하십시오
""")

if dcm is not None : 

    ds = dcmread(dcm)
    
    if ds.Modality == 'CT' :
        y_ratio, x_ratio = ds.PixelSpacing
    
    else : 
    
        y_ratio, x_ratio = ds.ImagerPixelSpacing

    ds_array= ds.pixel_array

    ds_array = cv2.normalize(ds_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    ds_array = np.dstack([ds_array,ds_array,ds_array])

    cv2.imwrite(os.path.join('ds_array.jpg'), ds_array)
    # # ds_array = np.divide(ds_array, ds_array.max())
    # ds_array = ds_array.astype(np.uint8)
    # Image.fromarray(ds_array).save('ds_array.jpg','JPEG') 

    # st.image(ds_array, caption=None, width=None, clamp=True)


    with Image.open("ds_array.jpg") as img:
        draw = ImageDraw.Draw(img) 
               

        # Draw an ellipse at each coordinate in points
        for point in st.session_state["points"][:6]:
            
            coords = get_ellipse_coords(point)
            draw.ellipse(coords, fill="red")

            if len(st.session_state["points"]) > 2 and len(st.session_state["points"]) < 6 : 
                for point in st.session_state["points"][3:]:
                    coords = get_ellipse_coords(point)
                    draw.ellipse(coords, fill="blue")

                p1 = st.session_state["points"][0]
                p2 = st.session_state["points"][1]
                p3 = st.session_state["points"][2]
                c1, radius1 = define_circle(p1,p2,p3)

                draw.ellipse((c1[0]-radius10, c1[1]-radius10, c1[0]+radius10, c1[1]+radius10), outline = 'red')
                draw.ellipse((c1[0]-radius1, c1[1]-radius1, c1[0]+radius1, c1[1]+radius1), outline = 'red')

            elif len(st.session_state["points"]) >= 6 : 
                for point in st.session_state["points"][3:6]:
                    coords = get_ellipse_coords(point)
                    draw.ellipse(coords, fill="blue")

                p1 = st.session_state["points"][0]
                p2 = st.session_state["points"][1]
                p3 = st.session_state["points"][2]
                c1, radius1 = define_circle(p1,p2,p3)
                # st.write(c1, radius1)
                draw.ellipse((c1[0]-radius10, c1[1]-radius10, c1[0]+radius10, c1[1]+radius10), outline = 'red')
                draw.ellipse((c1[0]-radius1, c1[1]-radius1, c1[0]+radius1, c1[1]+radius1), outline = 'red')

                p4 = st.session_state["points"][3]
                p5 = st.session_state["points"][4]
                p6 = st.session_state["points"][5]
                c2, radius2 = define_circle(p4,p5,p6)

                draw.ellipse((c2[0]-radius10, c2[1]-radius10, c2[0]+radius10, c2[1]+radius10), outline = 'blue')
                draw.ellipse((c2[0]-radius2, c2[1]-radius2, c2[0]+radius2, c2[1]+radius2), outline = 'blue')

                dist = math.sqrt(((c1[0] - c2[0])*x_ratio)**2 + ((c1[1] - c2[1])*y_ratio)**2)

                draw.line((c1[0],c1[1],c2[0],c2[1]), fill='green', width =5)
                font = ImageFont.truetype("Gidole-Regular.ttf", size=25)
                draw.text((c1[0],c1[1]+min(radius1,radius2)), f"{dist:.2f}mm", font = font)
                
        if st.sidebar.button("◀") :
            st.session_state["points"]= st.session_state["points"][:-1]
            st.experimental_rerun()
        if st.sidebar.button("⟳") : 
            st.session_state["points"]= []
            st.experimental_rerun()
                
        value = streamlit_image_coordinates(img, key="pil")

        if value is not None:
            # st.write(f'{len(st.session_state["points"])}')
            point = value["x"], value["y"]  
            if point not in st.session_state["points"]:

                st.write(point)
                st.session_state["points"].append(point)
                st.write(f'{(st.session_state["points"])}')
                st.experimental_rerun()
                
        
            # st.experimental_rerun()



        