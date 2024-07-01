from utils_func import *
import pydicom
from pydicom import dcmread
from pydicom.data import get_testdata_file
from pydicom.pixel_data_handlers.util import apply_voi_lut
# from streamlit_modal import Modal
import streamlit.components.v1 as components

import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

from PIL import Image, ImageDraw, ImageFont
import cv2

import math
radius10 = 2
st.set_page_config(layout="wide")

drawing_mode = st.sidebar.radio(
    "Annotation tool:",
    ("3-point circle only","Cobbs angle", "2-point and radius"))

if "points_3point" not in st.session_state:
    st.session_state["points_3point"] = []
    
if "points_length" not in st.session_state:
    st.session_state["points_cobbs"] = []
    
if "points_2point" not in st.session_state:
    st.session_state["points_2point"] = []
    
# if "points_cobbs" not in st.session_state:
#     st.session_state["points_cobbs"] = []


st.header('Hinge joint sagittal plane view')
dcm = st.file_uploader("X-ray, CT Dicom",
                      help="""
Ankle X-ray를 Upload 하십시오
""")

def read_dicom(dcm): 
    ds = dcmread(dcm)
    ds_array= ds.pixel_array
    ds_array = cv2.normalize(ds_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    ds_array = np.dstack([ds_array,ds_array,ds_array])
    cv2.imwrite(os.path.join('ds_array.jpg'), ds_array)
    
    try : 
        y_ratio, x_ratio = ds[0x0028, 0x0030].value
        open_modal = False
            
    except : 
        y_ratio, x_ratio = 0.145, 0.145
        open_modal = True
        print('실패')
        
            
    return ds_array, y_ratio, x_ratio, open_modal
        
        

if dcm is not None : 
    
    ds_array, y_ratio, x_ratio, open_modal = read_dicom(dcm)
    st.sidebar.number_input("X axis mm/pixel 비율", value = x_ratio)
    st.sidebar.number_input("Y axis mm/pixel 비율", value = y_ratio)
    
    H, W, _ = ds_array.shape
    
    if open_modal == True : 
        st.write("dicom file 에 mm/pixel 비율이 파악되지 않아 확인필요합니다, default = 0.145, 0.145로 반영합니다. sidebar를 확인해주세요")
        txt = st.sidebar.text_area('해당 data에서 비율 data에 대한 검토가 필요합니다', value = f'{dcmread(dcm, force=True)}',max_chars = None)
        # st.sidebar.write(txt)
    
    # open_modal = True
        
#     if open_modal:
#         modal.open()
    
#     if modal.is_open():
#         with modal.container():
#             st.write("")
#             # st.write("dicom file 에 mm/pixel 비율이 파악되지 않아 확인필요합니다, default = 0.145, 0.145로 반영합니다")
# #             st.write("Text goes here")

# #             html_string = '''
# #             <h1>HTML string in RED</h1>

# #             <script language="javascript">
# #               document.querySelector("h1").style.color = "red";
# #             </script>
# #             '''
# #             components.html(html_string)

# #             st.write("Some fancy text")
# #             value = st.checkbox("Check me")
# #             st.write(f"Checkbox checked: {value}")
    #######################################################
    # ds = dcmread(dcm)
#     ds_array= ds.pixel_array
#     ds_array = cv2.normalize(ds_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
#     ds_array = np.dstack([ds_array,ds_array,ds_array])
    
#     try : 
#         if ds.Modality == 'CT' :
#             y_ratio, x_ratio = ds.PixelSpacing 
#         else : 
#             y_ratio, x_ratio = ds.ImagerPixelSpacing
            
#     except : 
#         y_ratio, x_ratio = 0.145, 0.145
#         open_modal = True
        
#         if open_modal:
#             modal.open()
        
#         if modal.is_open():
#             with modal.container():
#                 # st.write("dicom file 에 mm/pixel 비율이 파악되지 않아 확인필요합니다, default = 0.145, 0.145로 반영합니다")
#                 st.markdown("Text goes here")

#                 html_string = '''
#                 <h1>HTML string in RED</h1>

#                 <script language="javascript">
#                   document.querySelector("h1").style.color = "red";
#                 </script>
#                 '''
#                 components.html(html_string)

#                 st.write("Some fancy text")
#                 value = st.checkbox("Check me")
#                 st.write(f"Checkbox checked: {value}")

####################################################################

    with Image.open("ds_array.jpg") as img:
        getback = st.sidebar.button("◀")
        refresh = st.sidebar.button("⟳")
        
        draw = ImageDraw.Draw(img) 

        # Draw an ellipse at each coordinate in points
        for point in st.session_state["points_3point"][:6]:

            coords = get_ellipse_coords(point)
            draw.ellipse(coords, fill="red")

            if len(st.session_state["points_3point"]) > 2 and len(st.session_state["points_3point"]) < 6 : 
                for point in st.session_state["points_3point"][3:]:
                    coords = get_ellipse_coords(point)
                    draw.ellipse(coords, fill="blue")

                p1 = st.session_state["points_3point"][0]
                p2 = st.session_state["points_3point"][1]
                p3 = st.session_state["points_3point"][2]
                c1, radius1 = define_circle(p1,p2,p3)

                draw.ellipse((c1[0]-radius10, c1[1]-radius10, c1[0]+radius10, c1[1]+radius10), outline = 'red')
                draw.ellipse((c1[0]-radius1, c1[1]-radius1, c1[0]+radius1, c1[1]+radius1), outline = 'red')

            elif len(st.session_state["points_3point"]) >= 6 : 
                for point in st.session_state["points_3point"][3:6]:
                    coords = get_ellipse_coords(point)
                    draw.ellipse(coords, fill="blue")

                p1 = st.session_state["points_3point"][0]
                p2 = st.session_state["points_3point"][1]
                p3 = st.session_state["points_3point"][2]
                c1, radius1 = define_circle(p1,p2,p3)
                # st.write(c1, radius1)
                draw.ellipse((c1[0]-radius10, c1[1]-radius10, c1[0]+radius10, c1[1]+radius10), outline = 'red')
                draw.ellipse((c1[0]-radius1, c1[1]-radius1, c1[0]+radius1, c1[1]+radius1), outline = 'red')

                p4 = st.session_state["points_3point"][3]
                p5 = st.session_state["points_3point"][4]
                p6 = st.session_state["points_3point"][5]
                c2, radius2 = define_circle(p4,p5,p6)

                draw.ellipse((c2[0]-radius10, c2[1]-radius10, c2[0]+radius10, c2[1]+radius10), outline = 'blue')
                draw.ellipse((c2[0]-radius2, c2[1]-radius2, c2[0]+radius2, c2[1]+radius2), outline = 'blue')

                dist = math.sqrt(((c1[0] - c2[0])*x_ratio)**2 + ((c1[1] - c2[1])*y_ratio)**2)

                draw.line((c1[0],c1[1],c2[0],c2[1]), fill='green', width =5)
                font = ImageFont.truetype("Gidole-Regular.ttf", size=25)
                draw.text((c1[0],c1[1]+2*max(radius1,radius2)), f"{dist:.2f}mm", font = font)
                

        if getback :
            st.session_state["points_3point"]= st.session_state["points_3point"][:-1]
            st.rerun()
        if refresh : 
            st.session_state["points_length"]= []
            st.session_state["points_cobbs"] = []
            st.session_state["points_3point"]= []
            st.session_state["points_2point"]= []
            st.rerun()
        
#         if drawing_mode == 'Length' : 
#             # draw = ImageDraw.Draw(img) 
            
#             for point in st.session_state["points_length"]:
#                 coords = get_ellipse_coords(point)
#                 draw.ellipse(coords, fill="green")
                
#             if len(st.session_state["points_length"]) > 1 : 
#                 for i in range(len(st.session_state["points_length"])//2) :
#                     c1 = st.session_state["points_length"][2*i]
#                     c2 = st.session_state["points_length"][2*i+1]
#                     draw.line([c1,c2], fill='green', width = 1)
#                     dist = math.sqrt(((c1[0] - c2[0])*x_ratio)**2 + ((c1[1] - c2[1])*y_ratio)**2)
#                     font1 = ImageFont.truetype("Gidole-Regular.ttf", size=20)
#                     c3 = ((c1[0]+c2[0])/2,(c1[1]+c2[1])/2)
#                     draw.text(c3, f"{dist:.2f}mm", font = font1)
                
                
#             if getback :
#                 st.session_state["points_length"]= st.session_state["points_length"][:-1]
#                 st.experimental_rerun()
# #             if refresh : 
                
# #                 st.experimental_rerun()
                
                
#             value = streamlit_image_coordinates(img, width =700, key="pil")
#             if value is not None:
#                 # st.write(f'{len(st.session_state["points"])}')
#                 point = value["x"] * (W/700) , value["y"] * (W/700)
#                 if point not in st.session_state["points_length"]:
#                     st.session_state["points_length"].append(point)
#                     st.experimental_rerun() 
        
        elif drawing_mode == '2-point and radius' :
            value = None
            
            for point in st.session_state["points_2point"][:6]:

                coords = get_ellipse_coords(point)
                draw.ellipse(coords, fill="pink")

                # https://math.stackexchange.com/questions/1781438/finding-the-center-of-a-circle-given-two-points-and-a-radius-algebraically


                if len(st.session_state["points_2point"]) > 2 and len(st.session_state["points_2point"]) < 5 : 
                    for point in st.session_state["points_2point"][3:]:
                        coords = get_ellipse_coords(point)
                        draw.ellipse(coords, fill="purple")

                    p1 = st.session_state["points_2point"][0]
                    p2 = st.session_state["points_2point"][1]
                    p3 = st.session_state["points_2point"][2]

                    c1, radius1 = define_circle(p1,p2,p3)

                    draw.ellipse((c1[0]-radius10, c1[1]-radius10, c1[0]+radius10, c1[1]+radius10), outline = 'pink')
                    draw.ellipse((c1[0]-radius1, c1[1]-radius1, c1[0]+radius1, c1[1]+radius1), outline = 'pink')

                elif len(st.session_state["points_2point"]) >= 5 : 
                    for point in st.session_state["points_2point"][3:]:
                        coords = get_ellipse_coords(point)
                        draw.ellipse(coords, fill="purple")

                    p1 = st.session_state["points_2point"][0]
                    p2 = st.session_state["points_2point"][1]
                    p3 = st.session_state["points_2point"][2]
                    c1, radius_2point = define_circle(p1,p2,p3)
                    # st.write(c1, radius_2point)
                    draw.ellipse((c1[0]-radius10, c1[1]-radius10, c1[0]+radius10, c1[1]+radius10), outline = 'pink')
                    draw.ellipse((c1[0]-radius_2point, c1[1]-radius_2point, c1[0]+radius_2point, c1[1]+radius_2point), outline = 'pink')

                    p4 = st.session_state["points_2point"][3]
                    p5 = st.session_state["points_2point"][4]
                    # c2, radius2 = define_circle(p3,p4,p5)
                    
                    c2, c3 = define_circle_2(p4, p5, radius_2point)
                    
                    c2 = choice_point(c1,c2,c3)
                    

                    draw.ellipse((c2[0]-radius10, c2[1]-radius10, c2[0]+radius10, c2[1]+radius10), outline = 'purple')
                    # draw.ellipse((c2[0]-radius2, c2[1]-radius2, c2[0]+radius2, c2[1]+radius2), outline = 'purple')
                    
                    draw.ellipse((c2[0]-radius_2point, c2[1]-radius_2point, c2[0]+radius_2point, c2[1]+radius_2point), outline = 'purple')
                    # draw.ellipse((c3[0]-radius_2point, c3[1]-radius_2point, c3[0]+radius_2point, c3[1]+radius_2point), outline = 'purple')
                    

                    dist = math.sqrt(((c1[0] - c2[0])*x_ratio)**2 + ((c1[1] - c2[1])*y_ratio)**2)

                    draw.line((c1[0],c1[1],c2[0],c2[1]), fill='green', width =5)
                    font = ImageFont.truetype("Gidole-Regular.ttf", size=25)
                    draw.text((c1[0],c1[1]+2*max(radius_2point,radius_2point)), f"{dist:.2f}mm", font = font)   



                if getback :
                    st.session_state["points_2point"]= st.session_state["points_2point"][:-1]
                    st.rerun()
    #             if refresh : 

    #                 st.experimental_rerun()
                
                
            value = streamlit_image_coordinates(img, width =700, key="pil")
            if value is not None:
                # st.write(f'{len(st.session_state["points"])}')
                point = value["x"] * (W/700) , value["y"] * (W/700) 
                if point not in st.session_state["points_2point"]:
                    st.session_state["points_2point"].append(point)
                    st.rerun() 
        
        
                    
        elif drawing_mode == 'Cobbs angle' : 
            value = None
            for point in st.session_state["points_cobbs"]:
                coords = get_ellipse_coords(point)
                draw.ellipse(coords, fill="violet")
                
            if len(st.session_state["points_cobbs"]) > 1 : 
                
                for i in range(len(st.session_state["points_cobbs"])//2) :
                    c1 = st.session_state["points_cobbs"][2*i]
                    c2 = st.session_state["points_cobbs"][2*i+1]
                    draw.line([c1,c2], fill='violet', width = 2)
                    
                for i in range(len(st.session_state["points_cobbs"])//4) :
                    c1 = st.session_state["points_cobbs"][4*i]
                    c2 = st.session_state["points_cobbs"][4*i+1]
                    # draw.line([c1,c2], fill='violet', width = 2)
                    c3 = st.session_state["points_cobbs"][4*i+2]
                    c4 = st.session_state["points_cobbs"][4*i+3]
                    # draw.line([c3,c4], fill='violet', width = 2)
                    
                    c1y, c1x = c1
                    c2y, c2x = c2
                    c3y, c3x = c3
                    c4y, c4x = c4
                    
                    c5y = c1y + c3y - c4y
                    c5x = c1x + c3x - c4x
                    
                    c5 = c5y, c5x
                    
                    coords_c5 = get_ellipse_coords(point)
                    draw.ellipse(coords_c5, fill="indigo")
                    draw.line([c1,c5], fill='indigo', width = 2)
                    
                    font1 = ImageFont.truetype("Gidole-Regular.ttf", size=20)
                    # c5 = ((c1[0]+c2[0])/2,(c1[1]+c2[1])/2)
                    # draw.text(c3, f"{dist:.2f}mm", font = font1)
                
                
            if getback :
                st.session_state["points_cobbs"]= st.session_state["points_cobbs"][:-1]
                st.rerun()
#             if refresh : 
                
#                 st.experimental_rerun()
                
                
            value = streamlit_image_coordinates(img, key="pil")
            if value is not None:
                # st.write(f'{len(st.session_state["points"])}')
                point = value["x"], value["y"]  
                if point not in st.session_state["points_cobbs"]:
                    st.session_state["points_cobbs"].append(point)
                    st.rerun() 
        

        value = streamlit_image_coordinates(img, width =700, key="pil2")
        if value is not None:
            # st.write(f'{len(st.session_state["points"])}')
            point = value["x"] * (W/700) , value["y"] * (W/700)
            if point not in st.session_state["points_3point"]:
                st.session_state["points_3point"].append(point)
                st.rerun()

        
        # st.experimental_rerun()



        
    
