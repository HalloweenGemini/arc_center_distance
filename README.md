# Introduction

<details>
<summary>English</summary>
<br>

Hello, I am a resident in the Department of Orthopedic Surgery at Seoul National University Hospital.  
Arc center distance can be a useful parameter in assessing fractures in joints, such as ankle fractures or mallet fingers.  
(Kim, M. B., Lee, J. H., & Lee, Y. H. (2022). Arc center distance as a novel quantitative radiographic parameter for volar Barton fractures. Archives of Orthopaedic and Trauma Surgery, 142(12), 3765-3770. [https://doi.org/10.1007/s00402-021-04240-0](https://doi.org/10.1007/s00402-021-04240-0))  
This program helps you upload an X-ray (DICOM file), select three points that make up each joint, and measure the distance between the centers of each circle.

## Usage

1. Access [http://leejm1031.synology.me:8888](http://leejm1031.synology.me:8888)
2. Click "Browse files" or drag and drop an image to upload.
3. Click three points on a joint. Confirm that a circle is drawn and then click three points on another joint to draw the remaining circle.
4. The undo and refresh buttons are located on the sidebar.

* The length is measured based on the pixel-to-length ratio in the DICOM file, but sometimes this information is missing or stored differently in the DICOM file. In such cases, a warning may appear. Please contact jaeminlee.1996@gmail.com for modifications to improve future development.

## Executable file
A PyQT-based program has been released. The usage method is the same.
### Download
- [Downloadlink_MAC](https://github.com/HalloweenGemini/arc_center_distance/raw/main/acd_pyqt_v0.2.zip)
- [Downloadlink_WIN](https://github.com/HalloweenGemini/arc_center_distance/raw/main/acd_pyqt_v0.2.exe)


</details>

<details>
<summary>한국어</summary>
<br>

안녕하세요. 저는 서울대학교병원 정형외과 소속의 레지던트입니다.  
Ankle fracture나 mallet finger 등 관절에서의 골절에 있어서 정도를 판단하는데에 arc center distance는 useful parameter가 될 수 있습니다.  
(Kim, M. B., Lee, J. H., & Lee, Y. H. (2022). Arc center distance as a novel quantitative radiographic parameter for volar Barton fractures. Archives of Orthopaedic and Trauma Surgery, 142(12), 3765-3770. [https://doi.org/10.1007/s00402-021-04240-0](https://doi.org/10.1007/s00402-021-04240-0))  
이 프로그램은 X-ray를 업로드하고(DICOM 파일), 관절을 이루는 세 점씩 클릭하여 선택한 후에 각 원의 중심의 거리를 측정하는 데에 도움을 주는 프로그램입니다.

## 자세한 사용법

1. [http://leejm1031.synology.me:8888](http://leejm1031.synology.me:8888) 에 접속
2. Browse files를 누르거나, Drag and drop으로 이미지를 업로드합니다.
3. 한 관절에 대해 세 점을 클릭합니다. 원이 그려지는 것을 확인하고 다른 관절에 대해 세 점을 클릭하여 나머지 원이 그려지는 것을 확인합니다.
4. 되돌리는 버튼과 Refresh 버튼은 사이드바에 있습니다.

* DICOM 파일에서의 픽셀 : 길이 비율을 가지고 길이를 측정하지만 때에 따라 해당 정보가 없거나 파라미터가 다르게 저장되어있는 DICOM 파일도 있습니다. 그런 경우 경고창이 뜰 수 있으며 추후 개발을 위해 jaeminlee.1996@gmail.com 으로 연락주시면 변경하도록 하겠습니다.

## 실행파일 
PyQT 기반의 실행파일이 배포되었습니다. 
실행 방법은 동일합니다. 

### Download
- [Downloadlink_MAC](https://github.com/HalloweenGemini/arc_center_distance/raw/main/acd_pyqt_v0.2.zip)
- [Downloadlink_WIN](https://github.com/HalloweenGemini/arc_center_distance/raw/main/acd_pyqt_v0.2.exe)

</details>