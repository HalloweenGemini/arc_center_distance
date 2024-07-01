import numpy as np
import os
from pydicom import dcmread
from pydicom.data import get_testdata_file
from pydicom.pixel_data_handlers.util import apply_voi_lut
import streamlit as st
import math

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

def solve(a,b,c):
    """
    ax^2 + bx + c = 0 에서 x의 근    
    """
    D = b*b-4*a*c
    if D > 0 : 
        x1=round((-b-D**0.5)/2*a)
        x2=round((-b+D**0.5)/2*a)
        return x1, x2
    elif D==0:
        x=round(-b/2*a)
        return x, x
    else : 
        return None
    
def define_circle_2(p1, p2, r) : 
    """
    Returns the center and radius of the circle passing the given 2 points and radius
    """
    
    try : 
        x1, y1 = p1
        x2, y2 = p2
        q = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        y3 = (y1+y2)/2
        x3 = (x1+x2)/2
        basex = math.sqrt(math.pow(r,2)-math.pow((q/2),2))*((y1-y2)/q)
        basey = math.sqrt(math.pow(r,2)-math.pow((q/2),2))*((x2-x1)/q)
        
        centerx1 = x3 + basex
        centery1 = y3 + basey
        centerx2 = x3 - basex
        centery2 = y3 - basey
        
        return (centerx2, centery2), (centerx1, centery1)
        
#         if centery2 > centery1 :
#             return (centerx2, centery2)

#         if centery1 >= centery2 : 
#             return (centerx1, centery1)

    except : 
        return None
        
def choice_point(c1, c2, c3) : 
    '''
    c2, c3 중 c1에 더 가까운 것을 고른다
    
    '''
    x1, y1 = c1
    x2, y2 = c2 
    x3, y3 = c3 
    
    d12 = (x1-x2)**2 + (y1-y2)**2 
    d13 = (x1-x3)**2 + (y1-y2)**2 
    
    if d12 > d13 : 
        return c3
    
    else : return c2
        
    
# def define_circle_2(p1, p2, r) : 
#     """
#     Returns the center and radius of the circle passing the given 2 points and radius
#     """
    
#     try : 
#         x1, y1 = p1
#         x2, y2 = p2

#         a = (y1-y2)^2 + (x1-x2)^2
#         b = (-2)*x1*(y1-y2)^2 - (x1-x2)*(x1^2-x2^2-y1^2+2*y1*y2-y2^2)
#         c = (x1^2-r^2)*(y1-y2)^2 + (1/4)*(x1^2-x2^2-y1^2+2*y1*y2-y2^2)^2 

#         x3, x4 = solve(a,b,c)

#         e = (x2-x1)/(y1-y2)
#         f = (x1^2 -x2^2 + y1^2-y2^2)/(2*y1-2*y2)

#         y3, y4 = e*x3+f, 3*x4+f 

#         if y3 > y4 :
#             return x4, y4

#         if y4 >= y3 : 
#             return x3, y3
    
#     except : 
#         return None
    