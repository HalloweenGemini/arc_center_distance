import math
import numpy as np

def define_circle(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    temp = x2**2 + y2**2
    bc = (x1**2 + y1**2 - temp) / 2
    cd = (temp - x3**2 - y3**2) / 2
    det = (x1 - x2) * (y2 - y3) - (x2 - x3) * (y1 - y2)

    if abs(det) < 1.0e-10:
        raise ValueError("Points are collinear")

    cx = (bc * (y2 - y3) - cd * (y1 - y2)) / det
    cy = ((x1 - x2) * cd - (x2 - x3) * bc) / det
    radius = math.sqrt((cx - x1)**2 + (cy - y1)**2)

    return (cx, cy), radius

def define_circle_2(p1, p2, radius):
    x1, y1 = p1
    x2, y2 = p2

    q = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if q > 2 * radius:
        raise ValueError("Distance between points is greater than the diameter")

    x3 = (x1 + x2) / 2
    y3 = (y1 + y2) / 2

    d = math.sqrt(radius**2 - (q / 2)**2)
    c1 = (x3 + d * (y1 - y2) / q, y3 + d * (x2 - x1) / q)
    c2 = (x3 - d * (y1 - y2) / q, y3 - d * (x2 - x1) / q)

    return c1, c2

def choice_point(c1, c2, c3):
    dist2 = math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
    dist3 = math.sqrt((c1[0] - c3[0])**2 + (c1[1] - c3[1])**2)

    return c2 if dist2 < dist3 else c3