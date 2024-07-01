import sys
import os
import math
import numpy as np
import pydicom
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, QSizePolicy
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint

class DicomViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Dicom Viewer')
        self.setGeometry(100, 100, 800, 600)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()

        self.label = QLabel(self)
        self.label.setFixedSize(700, 500)

        self.openButton = QPushButton('Open DICOM', self)
        self.openButton.clicked.connect(self.openDicom)

        self.resetButton = QPushButton('Reset', self)
        self.resetButton.clicked.connect(self.resetPoints)

        self.undoButton = QPushButton('Undo', self)
        self.undoButton.clicked.connect(self.undoLastPoint)

        self.distanceLabel = QLabel("Distance: N/A", self)

        self.hbox.addWidget(self.openButton)
        self.hbox.addWidget(self.resetButton)
        self.hbox.addWidget(self.undoButton)
        self.hbox.addWidget(self.distanceLabel)

        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.label)

        self.main_widget.setLayout(self.vbox)

        self.points = []
        self.dcm_image = None
        self.ratio = (0.145, 0.145)

        self.show()

    def openDicom(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open DICOM File", "", "DICOM Files (*.dcm);;All Files (*)", options=options)
        if fileName:
            self.loadDicom(fileName)
            self.autoClickAndUndo()

    def loadDicom(self, fileName):
        ds = pydicom.dcmread(fileName)
        self.dcm_image = ds.pixel_array
        self.dcm_image = cv2.normalize(self.dcm_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        self.resetPoints()

        try:
            self.ratio = ds.PixelSpacing
        except AttributeError:
            try:
                self.ratio = ds.ImagerPixelSpacing
            except AttributeError:
                self.ratio = (0.145, 0.145)
                QMessageBox.warning(self, "Warning", "This image lacks pixel to length information. The length may not be accurate.")

        self.displayImage()

    def displayImage(self):
        if self.dcm_image is not None:
            height, width = self.dcm_image.shape
            bytesPerLine = 1 * width
            qImg = QImage(self.dcm_image.data, width, height, bytesPerLine, QImage.Format_Indexed8)
            qImg = qImg.scaled(self.label.size(), Qt.KeepAspectRatio)
            self.label.setPixmap(QPixmap.fromImage(qImg))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.label.underMouse() and self.dcm_image is not None:
            label_pos = self.label.mapFromGlobal(self.mapToGlobal(event.pos()))
            pixmap = self.label.pixmap()

            if pixmap is not None:
                pixmap_width = pixmap.width()
                pixmap_height = pixmap.height()
                label_width = self.label.width()
                label_height = self.label.height()

                x_scale = self.dcm_image.shape[1] / pixmap_width
                y_scale = self.dcm_image.shape[0] / pixmap_height

                img_x = label_pos.x() * x_scale
                img_y = label_pos.y() * y_scale

                if 0 <= img_x < self.dcm_image.shape[1] and 0 <= img_y < self.dcm_image.shape[0]:
                    self.points.append((img_x, img_y))
                    print(f"Clicked Point: {(img_x, img_y), event.pos().x(), event.pos().y()}")  # 좌표를 로그로 출력
                    print(x_scale, y_scale)
                    self.updateImage()
                    if len(self.points) == 6:
                        self.calculateDistance()

    def updateImage(self):
        if self.dcm_image is not None:
            img_copy = cv2.cvtColor(self.dcm_image.copy(), cv2.COLOR_GRAY2RGB)
            qImg = QImage(img_copy.data, img_copy.shape[1], img_copy.shape[0], img_copy.strides[0], QImage.Format_RGB888)
            qImg = qImg.scaled(self.label.size(), Qt.KeepAspectRatio)
            pixmap = QPixmap.fromImage(qImg)
            painter = QPainter(pixmap)

            pixmap_width = pixmap.width()
            pixmap_height = pixmap.height()

            x_scale = pixmap_width / self.dcm_image.shape[1]
            y_scale = pixmap_height / self.dcm_image.shape[0]

            for i, point in enumerate(self.points):
                color = Qt.red if i < 3 else Qt.blue
                painter.setPen(QPen(color, 2, Qt.SolidLine))
                scaled_point = QPoint(int(point[0] * x_scale), int(point[1] * y_scale))
                painter.drawEllipse(scaled_point, 1, 1)

            if len(self.points) >= 3:
                self.drawCircle(painter, self.points[:3], Qt.red)
            if len(self.points) == 6:
                self.drawCircle(painter, self.points[3:], Qt.blue)
                self.drawCenterLine(painter)

            painter.end()
            self.label.setPixmap(pixmap)

    def drawCircle(self, painter, points, color):
        c, r = self.define_circle(points[0], points[1], points[2])
        painter.setPen(QPen(color, 2, Qt.SolidLine))

        pixmap_width = self.label.pixmap().width()
        pixmap_height = self.label.pixmap().height()

        x_scale = pixmap_width / self.dcm_image.shape[1]
        y_scale = pixmap_height / self.dcm_image.shape[0]

        scaled_center = QPoint(int(c[0] * x_scale), int(c[1] * y_scale))
        scaled_radius = int(r * x_scale)  # Assuming isotropic scaling (x_scale == y_scale)

        painter.drawEllipse(scaled_center, scaled_radius, scaled_radius)
        print(f"Center: {scaled_center}, Radius: {scaled_radius}")

    def drawCenterLine(self, painter):
        if len(self.points) >= 6:
            c1, _ = self.define_circle(self.points[0], self.points[1], self.points[2])
            c2, _ = self.define_circle(self.points[3], self.points[4], self.points[5])

            pixmap_width = self.label.pixmap().width()
            pixmap_height = self.label.pixmap().height()

            x_scale = pixmap_width / self.dcm_image.shape[1]
            y_scale = pixmap_height / self.dcm_image.shape[0]

            scaled_c1 = QPoint(int(c1[0] * x_scale), int(c1[1] * y_scale))
            scaled_c2 = QPoint(int(c2[0] * x_scale), int(c2[1] * y_scale))

            painter.setPen(QPen(Qt.white, 2, Qt.SolidLine))
            painter.drawLine(scaled_c1, scaled_c2)
            print(f"Center Line: {scaled_c1} to {scaled_c2}")

    def calculateDistance(self):
        if len(self.points) >= 6:
            p1, p2, p3 = self.points[:3]
            p4, p5, p6 = self.points[3:6]

            c1, r1 = self.define_circle(p1, p2, p3)
            c2, r2 = self.define_circle(p4, p5, p6)

            print(self.ratio)
            # c1, c2 are in pixel unit. Convert them to mm unit
            

            dist = math.sqrt(((c1[0] - c2[0]) * self.ratio[0]) ** 2 + ((c1[1] - c2[1]) * self.ratio[1]) ** 2)
            self.distanceLabel.setText(f"Distance: {dist:.2f} mm")


    def define_circle(self, p1, p2, p3):
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

    def resetPoints(self):
        self.points = []
        self.distanceLabel.setText("Distance: N/A")
        self.displayImage()

    def undoLastPoint(self):
        if self.points:
            self.points.pop()
            self.updateImage()

    def autoClickAndUndo(self):
        # 자동으로(0,0)을 찍고 undo
        self.points.append((0, 0))
        self.undoLastPoint()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = DicomViewer()
    sys.exit(app.exec_())