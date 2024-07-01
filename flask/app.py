from flask import Flask, render_template, request, jsonify
import pydicom
import cv2
import numpy as np
import base64
from dicom_utils import define_circle, define_circle_2, choice_point

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '선택된 파일이 없습니다'}), 400
    
    if file:
        ds = pydicom.dcmread(file)
        image = ds.pixel_array
        image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        _, buffer = cv2.imencode('.png', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        try:
            pixel_spacing = list(map(float, ds.PixelSpacing))
        except AttributeError:
            try:
                pixel_spacing = list(map(float, ds.ImagerPixelSpacing))
            except AttributeError:
                pixel_spacing = [0.145, 0.145]
                
        return jsonify({
            'image': image_base64,
            'pixelSpacing': pixel_spacing
        })

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    points = data['points']
    mode = data['mode']
    pixel_spacing = data['pixelSpacing']
    
    if mode == '3+3' and len(points) == 6:
        c1, r1 = define_circle(points[0], points[1], points[2])
        c2, r2 = define_circle(points[3], points[4], points[5])
        dist = ((c1[0] - c2[0]) * pixel_spacing[0])**2 + ((c1[1] - c2[1]) * pixel_spacing[1])**2
        dist = np.sqrt(dist)
    elif mode == '3+2' and len(points) == 5:
        c1, radius1 = define_circle(points[0], points[1], points[2])
        c2, c3 = define_circle_2(points[3], points[4], radius1)
        chosen_center = choice_point(c1, c2, c3)
        dist = ((c1[0] - chosen_center[0]) * pixel_spacing[0])**2 + ((c1[1] - chosen_center[1]) * pixel_spacing[1])**2
        dist = np.sqrt(dist)
    else:
        return jsonify({'error': '잘못된 모드 또는 점의 개수'}), 400
    
    return jsonify({'distance': float(dist)})

if __name__ == '__main__':
    app.run(debug=True)